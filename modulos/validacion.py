 
import re
from datetime import date, datetime, timedelta
 
 
PATRONES = {
    "CC": re.compile(r"^\d{6,10}$"),
    "CE": re.compile(r"^(?:\d{6,10}|[A-Za-z]\d{6,9})$"),
    "PA": re.compile(r"^(?=.*[A-Za-z])[A-Za-z0-9]{6,12}$"),
    "centro": re.compile(r"^CC-\d{4}$")
}
 
 
def convertir_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
 
    if isinstance(valor, date):
        return valor
 
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(
                str(valor).strip(), formato
            ).date()
        except (ValueError, TypeError):
            pass
 
    return None
 
 
def obtener_parametros(configuracion):
    parametros = configuracion.get("parametros", {})
 
    if isinstance(parametros, dict):
        return parametros
 
    # Compatibilidad por si los parámetros llegan como lista.
    resultado = {}
 
    for fila in parametros:
        if isinstance(fila, dict) and fila.get("clave") is not None:
            resultado[str(fila["clave"]).strip()] = fila.get("valor")
 
    return resultado
 
 
def validar_novedad(novedad, configuracion):
    errores = []
 
    if not isinstance(novedad, dict):
        return ["La novedad debe ser un objeto JSON."]
 
    tipo = str(novedad.get("tipo", "")).strip().upper()
    obligatorios = {}
 
    for fila in configuracion.get("campos_requeridos", []):
        clave = str(
            fila.get("tipo_novedad", "")
        ).strip().upper()
 
        obligatorios[clave] = str(
            fila.get("campos_requeridos", "") or ""
        ).split(";")
 
    if tipo not in obligatorios:
        return ["Tipo de novedad no reconocido."]
 
    for campo in obligatorios[tipo]:
        campo = campo.strip()
 
        if campo and (
            novedad.get(campo) is None
            or str(novedad.get(campo)).strip() == ""
        ):
            errores.append("Falta el campo obligatorio: " + campo)
 
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
            errores.append("El centro de costo no existe.")
 
    fecha = convertir_fecha(novedad.get("fecha_efectiva", ""))
 
    if fecha is None:
        errores.append("La fecha efectiva no es valida.")
 
    else:
        hoy = date.today()
        parametros = obtener_parametros(configuracion)
 
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
 
    telefono = re.sub(
        r"\D", "", str(novedad.get("telefono", "") or "")
    )
 
    if telefono:
        parametros = obtener_parametros(configuracion)
 
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
 
    cargo = str(novedad.get("cargo", "") or "").strip()

    if cargo and not any(
        str(fila.get("codigo_cargo", "")).strip() == cargo
        for fila in configuracion.get("cargos", [])
    ):
        errores.append("El cargo no existe.")
 
    return errores
 