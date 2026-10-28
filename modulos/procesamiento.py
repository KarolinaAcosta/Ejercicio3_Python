import re
import unicodedata
 
from modulos.validacion import validar_novedad, convertir_fecha
 
 
def normalizar_texto(texto):
    return " ".join(str(texto or "").split()).title()
 
 
def buscar_fila(filas, campo, valor):
    for fila in filas:
        if str(fila.get(campo, "")).strip() == str(valor).strip():
            return fila
 
    return None
 
 
def crear_correo(nombres, apellidos, dominio):
    nombres = normalizar_texto(nombres).split()
    apellidos = normalizar_texto(apellidos).split()
 
    if not nombres or not apellidos:
        return ""
 
    texto = nombres[0] + "." + apellidos[0]
    texto = unicodedata.normalize("NFD", texto.lower())
 
    texto = "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )
 
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z.]", "", texto)
 
    return texto + "@" + str(dominio).strip()
 
 
def procesar_novedades(datos, configuracion):
    aceptados = []
    rechazados = []
    colisiones = []
    correos_usados = set()
 
    parametros = {}
 
    parametros = configuracion.get("parametros",[])
    dominio = parametros.get("dominio_correo","empresa.com")
 
    dominio = parametros.get("dominio_correo", "empresa.com")
 
    for novedad in datos.get("novedades", []):
        novedad = novedad.copy()
 
        if "tipo" not in novedad:
            novedad["tipo"] = novedad.get("tipo_novedad", "")
 
        if "centro_costo" not in novedad:
            novedad["centro_costo"] = novedad.get("centro_costos", "")
 
        tipo = str(novedad.get("tipo", "")).strip().upper()
 
        nombres = normalizar_texto(novedad.get("nombres", ""))
        apellidos = normalizar_texto(novedad.get("apellidos", ""))
        documento = novedad.get("numero_documento", "")
 
        nombre_completo = (nombres + " " + apellidos).strip()
        errores = validar_novedad(novedad, configuracion)
 
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
 
        cargo = str(novedad.get("cargo", "") or "").strip()
        centro = str(novedad.get("centros_costo", "") or "").strip()
 
        fila_cargo = buscar_fila(
            configuracion.get("Cargos", []),
            "codigo_cargo", cargo
        )
 
        fila_centro = buscar_fila(
            configuracion.get("Centros_Costo", []),
            "codigo", centro
        )
 
        nombre_cargo = fila_cargo.get("nombre_cargo", "") if fila_cargo else ""
        nivel = fila_cargo.get("nivel", "") if fila_cargo else ""
        area = str(fila_cargo.get("area", "") or "").strip() if fila_cargo else ""
        area_centro = str(fila_centro.get("area", "") or "").strip() if fila_centro else ""
 
        perfil = ""
        aprobacion = ""
 
        if cargo and tipo in ("ALTA", "CAMBIO_CARGO"):
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
 
            for fila in configuracion.get("Matriz_Roles", []):
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
 
            perfil = rol.get("perfil_sistema", "")
            aprobacion = rol.get("requiere_aprobacion", "")
 
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
 
        fecha = convertir_fecha(
            novedad.get("fecha_efectiva", "")
        )
 
        telefono = re.sub(
            r"\D", "", str(novedad.get("telefono", "") or "")
        )
 
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
 
    return aceptados, rechazados, colisiones