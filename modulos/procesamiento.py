import re
import unicodedata
 
from modulos.validacion import validar_novedad, convertir_fecha
 
 
def normalizar_texto(texto):
    """Quita espacios sobrantes y deja cada palabra con inicial mayúscula."""
    return " ".join(str(texto or "").split()).title()
 
 
def buscar_fila(filas, campo, valor):
    """Devuelve la primera fila cuyo valor coincida con el buscado."""
    for fila in filas:
        if str(fila.get(campo, "")).strip() == str(valor).strip():
            return fila
 
    return None
 

def crear_correo(nombres, apellidos, dominio):
    """Genera un correo con el primer nombre y apellido, normalizado y sin tildes."""
    nombres = normalizar_texto(nombres).split()
    apellidos = normalizar_texto(apellidos).split()
 
    # No se genera una dirección si falta el nombre o el apellido.
    if not nombres or not apellidos:
        return ""
 
    # Construir el usuario del correo y descomponer los caracteres acentuados.
    texto = nombres[0] + "." + apellidos[0]
    texto = unicodedata.normalize("NFD", texto.lower())
 
    # Eliminar las marcas de acento y los caracteres que no sean letras o puntos.
    texto = "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )
 
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z.]", "", texto)
 
    # Añadir el dominio corporativo al usuario generado.
    return texto + "@" + str(dominio).strip()
 
 
def procesar_novedades(datos, configuracion):
    """Valida las novedades y devuelve aceptadas, rechazadas y colisiones de correo."""
    # Preparar las listas de resultados y el control de correos ya asignados.
    aceptados = []
    rechazados = []
    colisiones = []
    correos_usados = set()
 
    # Leer de la configuración el dominio que se usará para los correos nuevos.
    parametros = {}
 
    parametros = configuracion.get("parametros",[])
    dominio = parametros.get("dominio_correo","empresa.com")
 
    dominio = parametros.get("dominio_correo", "empresa.com")
 
    # Recorrer las novedades sin modificar los diccionarios originales recibidos.
    for novedad in datos.get("novedades", []):
        novedad = novedad.copy()

        # Aceptar los nombres alternativos de tipo y centro, y unificarlos.
        tipo = str(
            novedad.get("tipo_novedad",novedad.get("tipo",""))
        ).strip().upper()

        centro = str(
            novedad.get("centro_costos",novedad.get("centro_costo",""))or""
        ).strip()

        novedad["tipo"]=tipo
        novedad["centro_costo"]=centro
 
        # Mantener los valores en las claves estándar que utiliza la validación.
        if "tipo" not in novedad:
            novedad["tipo"] = novedad.get("tipo_novedad", "")
 
        if "centro_costo" not in novedad:
            novedad["centro_costo"] = novedad.get("centro_costos", "")

        nombres = normalizar_texto(novedad.get("nombres", ""))
        apellidos = normalizar_texto(novedad.get("apellidos", ""))
        documento = novedad.get("numero_documento", "")
        
        # Preparar el nombre para el reporte y validar los datos de entrada.
        nombre_completo = (nombres + " " + apellidos).strip()
        
        errores = validar_novedad(novedad, configuracion)
 
        nombre_completo = (nombres + " " + apellidos).strip()
        errores = validar_novedad(novedad, configuracion)
        print("TIPO:", novedad.get("tipo"))
        print("CARGO:", novedad.get("cargo"))
        print("CENTRO:", novedad.get("centro_costo"))
        print("ERRORES:", errores)
        print("-" * 40)
 
        # Registrar los errores de validación y pasar a la siguiente novedad.
        if errores:
            rechazados.append({
                "consecutivo": novedad.get("consecutivo", ""),
                "tipo": tipo,
                "numero_documento": documento,
                "nombre": nombre_completo,
                "clasificacion": "VALIDACION",
                "campo": "",
                "motivo": "; ".join(errores),
                "valor_recibido": ""
            })
            continue
 
        # Buscar los datos descriptivos del cargo y del centro en la configuración.
        cargo = str(novedad.get("cargo", "") or "").strip()
        centro = str(novedad.get("centro_costo", "") or "").strip()
 
        fila_cargo = buscar_fila(
         configuracion.get("cargos", []),
         "codigo_cargo", cargo
        )
 
        fila_centro = buscar_fila(
            configuracion.get("centros_costo", []),
            "codigo", centro
        )
 
        nombre_cargo = fila_cargo.get("nombre_cargo", "") if fila_cargo else ""
        nivel = fila_cargo.get("nivel", "") if fila_cargo else ""
        area = str(fila_cargo.get("area", "") or "").strip() if fila_cargo else ""
        area_centro = str(fila_centro.get("area", "") or "").strip() if fila_centro else ""
 
        perfil = ""
        aprobacion = ""
 
        # Aplicar las reglas de área y perfil para altas o cambios de cargo.
        if cargo and tipo in ("ALTA", "CAMBIO_CARGO"):
            # Rechazar si el cargo y el centro de costo pertenecen a áreas distintas.
            if area and area_centro and area != area_centro:
                rechazados.append({
                    "consecutivo": novedad.get("consecutivo", ""),
                    "tipo": tipo,
                    "numero_documento": documento,
                    "nombre": nombre_completo,
                    "clasificacion": "REGLA_NEGOCIO",
                    "campo": "centros_costo",
                    "motivo": "El area del cargo no coincide con el centro de costo.",
                    "valor_recibido": centro
                })
                continue
 
            rol = None
 
            # Encontrar en la matriz el perfil asociado al cargo y al área.
            for fila in configuracion.get("matriz_roles", []):
                if (
                    str(fila.get("codigo_cargo", "")).strip() == cargo
                    and str(fila.get("area", "")).strip() == area
                ):
                    rol = fila
                    break
 
            if rol is None:
                rechazados.append({
                    "consecutivo": novedad.get("consecutivo", ""),
                    "tipo": tipo,
                    "numero_documento": documento,
                    "nombre": nombre_completo,
                    "clasificacion": "REGLA_NEGOCIO",
                    "campo": "cargo",
                    "motivo": "No existe combinacion de cargo y area en la matriz de roles.",
                    "valor_recibido": cargo
                })
                continue
 
            # Incorporar al registro el perfil y si requiere aprobación.
            perfil = rol.get("perfil_sistema", "")
            aprobacion = rol.get("requiere_aprobacion", "")
 
        # Crear correo para altas y agregar un sufijo si ya se asignó el mismo.
        correo = ""
 
        if tipo == "ALTA":
            correo_base = crear_correo(nombres, apellidos, dominio)
            correo = correo_base
            numero = 2
 
            while correo and correo in correos_usados:
                correo = (
                    correo_base.split("@")[0]
                    + str(numero) + "@" + dominio
                )
                numero += 1
 
            if correo and correo != correo_base:
                colisiones.append({
                    "correo_base": correo_base,
                    "correo_asignado": correo
                })
 
            if correo:
                correos_usados.add(correo)
 
        # Normalizar la fecha efectiva y dejar el teléfono únicamente con dígitos.
        fecha = convertir_fecha(
            novedad.get("fecha_efectiva", "")
        )
 
        telefono = re.sub(
            r"\D", "", str(novedad.get("telefono", "") or "")
        )
 
        # Guardar los datos aceptados con las columnas esperadas por el reporte.
        aceptados.append({
            "consecutivo": novedad.get("consecutivo", ""),
            "tipo_novedad": tipo,
            "tipo_documento": novedad.get("tipo_documento", ""),
            "numero_documento": documento,
            "nombre_completo": nombre_completo,
            "correo_corporativo": correo,
            "codigo_cargo": cargo,
            "nombre_cargo": nombre_cargo,
            "nivel": nivel,
            "centros_costo": centro,
            "area": area,
            "perfil_sistema": perfil,
            "requiere_aprobacion": aprobacion,
            "fecha_efectiva": fecha if fecha else "",
            "telefono": telefono,
            "fecha_vinculacion_previa": ""
        })
 
    # Entregar las tres listas para que el módulo de reporte las exporte.
    return aceptados, rechazados, colisiones