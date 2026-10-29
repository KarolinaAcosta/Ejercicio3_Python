 
import re
from datetime import date, datetime, timedelta
 
 
# Expresiones regulares para validar documentos y códigos de centro de costo.
PATRONES = {
    "CC": re.compile(r"^\d{6,10}$"),
    "CE": re.compile(r"^(?:\d{6,10}|[A-Za-z]\d{6,9})$"),
    "PA": re.compile(r"^(?=.*[A-Za-z])[A-Za-z0-9]{6,12}$"),
    "centro": re.compile(r"^CC-\d{4}$")
}
 

def convertir_fecha(valor):
    """Convierte una fecha reconocida a date; devuelve None si no puede interpretarla."""
    # Los objetos de fecha existentes no necesitan analizarse como texto.
    if isinstance(valor, datetime):
        return valor.date()
 
    if isinstance(valor, date):
        return valor
 
    # Aceptar los dos formatos de fecha usados por los archivos de entrada.
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(
                str(valor).strip(), formato
            ).date()
        except (ValueError, TypeError):
            pass
 
    return None
 
 # Devuelve los parámetros como diccionario, admitiendo el formato de lista.
def obtener_parametros(configuracion):
    parametros = configuracion.get("parametros", {})
 
    # La configuración normalmente ya contiene los parámetros como diccionario.
    if isinstance(parametros, dict):
        return parametros
 
    # Compatibilidad por si los parámetros llegan como lista.
    resultado = {}
 
    # Convertir filas con clave y valor al formato clave: valor.
    for fila in parametros:
        if isinstance(fila, dict) and fila.get("clave") is not None:
            resultado[str(fila["clave"]).strip()] = fila.get("valor")
 
    return resultado
 

def validar_novedad(novedad, configuracion):
    """Reúne y devuelve los errores de formato, campos y reglas de la novedad."""
    errores = []
 
    # El resto de las comprobaciones espera un registro representado como diccionario.
    if not isinstance(novedad, dict):
        return ["La novedad debe ser un objeto JSON."]
 
    # Cargar qué campos son obligatorios para el tipo de novedad recibido.
    tipo = str(novedad.get("tipo", "")).strip().upper()
    obligatorios = {}
 
    for fila in configuracion.get("campos_requeridos", []):
        clave = str(
            fila.get("tipo_novedad", "")
        ).strip().upper()
 
        obligatorios[clave] = str(
            fila.get("campos_requeridos", "") or ""
        ).split(";")
 
    # No se puede validar una novedad si su tipo no está en la configuración.
    if tipo not in obligatorios:
        return ["Tipo de novedad no reconocido."]
 
    # Reportar cada campo requerido que falte o esté vacío.
    for campo in obligatorios[tipo]:
        campo = campo.strip()
 
        if campo and (
            novedad.get(campo) is None
            or str(novedad.get(campo)).strip() == ""
        ):
            errores.append("Falta el campo obligatorio: " + campo)
 
    # Comprobar que el tipo de documento sea admitido y que el número coincida.
    tipo_doc = str(
        novedad.get("tipo_documento", "")
    ).strip().upper()
 
    documento = str(
        novedad.get("numero_documento", "")
    ).strip()
 
    if tipo_doc:
        if tipo_doc not in ("CC", "CE", "PA"):
            errores.append("Tipo de documento no valido.")
 
        elif documento and not PATRONES[tipo_doc].fullmatch(documento):
            errores.append("Numero de documento invalido.")
 
    elif documento:
        errores.append("Falta el tipo de documento.")
 
    # Revisar tanto el formato del centro como su presencia en el catálogo.
    centro = str(
        novedad.get("centro_costo", "") or ""
    ).strip()
 
    if centro:
        if not PATRONES["centro"].fullmatch(centro):
            errores.append("Formato de centro de costo invalido.")
 
        elif not any(
            str(fila.get("codigo", "")).strip() == centro
            for fila in configuracion.get("centros_costo", [])
        ):
            errores.append(
                f"El centro de costos {centro} no existe en la configuracion.")
 
    # Validar que la fecha exista, no esté en el pasado y respete el límite futuro.
    fecha = convertir_fecha(novedad.get("fecha_efectiva", ""))
 
    if fecha is None:
        errores.append("La fecha efectiva no es valida.")
 
    else:
        hoy = date.today()
        parametros = obtener_parametros(configuracion)
 
        # Usar el límite configurado y conservar 90 días como valor alternativo.
        try:
            max_dias = int(
                parametros.get("dias_maximo_futuro", 90)
            )
        except (ValueError, TypeError):
            max_dias = 90
 
        if fecha < hoy:
            errores.append("La fecha efectiva esta en el pasado.")
 
        elif fecha > hoy + timedelta(days=max_dias):
            errores.append(
                "La fecha supera el maximo de dias permitido."
            )
 
    # Quitar separadores del teléfono para contar solo sus dígitos.
    telefono = re.sub(
        r"\D", "", str(novedad.get("telefono", "") or "")
    )
 
    if telefono:
        parametros = obtener_parametros(configuracion)
 
        # Comparar la cantidad de dígitos con la longitud definida en parámetros.
        try:
            longitud = int(
                parametros.get("longitud_telefono", 10)
            )
        except (ValueError, TypeError):
            longitud = 10
 
        if len(telefono) != longitud:
            errores.append(
                "El telefono debe tener "
                + str(longitud) + " digitos."
            )
 
    # Confirmar que el código de cargo exista en el catálogo configurado.
    cargo = str(novedad.get("cargo", "") or "").strip()

    if cargo and not any(
        str(fila.get("codigo_cargo", "")).strip() == cargo
        for fila in configuracion.get("cargos", [])
    ):
        errores.append("El cargo no existe.")
 
    # Devolver todos los errores encontrados para que el procesamiento decida.
    return errores
 