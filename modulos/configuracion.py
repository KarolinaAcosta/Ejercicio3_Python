from pathlib import Path 
from openpyxl import load_workbook
 
from modulos.excepciones import ErrorConfiguracion
 
 
# Ubicación principal del proyecto.
RUTA_PROYECTO = Path(__file__).resolve().parent.parent  # Sube dos niveles hasta la carpeta principal del proyecto.
 
# Hojas que deben existir en el archivo Excel.
HOJAS_REQUERIDAS = [
    "Parametros",
    "cargos",
    "centros_costo",
    "matriz_roles",
    "campos_requeridos"
]
 
 
def leer_tabla(hoja, columnas_requeridas): 
    """
    Lee una hoja de Excel y devuelve sus filas como una lista
    de diccionarios.
    """
 
    encabezados = []
 
    # Leer los nombres de las columnas de la primera fila.
    for celda in hoja[1]:
        if celda.value is not None:
            encabezados.append(str(celda.value).strip())
        else:
            encabezados.append("")
 
    # Comprobar que existan las columnas necesarias.
    for columna in columnas_requeridas:
        if columna not in encabezados:
            raise ErrorConfiguracion(
                f"Falta la columna '{columna}' "
                f"en la hoja '{hoja.title}'."
            )
 
    registros = []
 
    # Leer las filas que contienen datos.
    for fila in hoja.iter_rows(min_row=2, values_only=True): # iter_rows recorre filas; min_row=2 empieza en la segunda y values_only devuelve valores.
 
        # Ignorar las filas completamente vacías.
        if all(valor is None for valor in fila):
            continue
 
        registro = {}  # Se crea vacío y luego se agregan sus columnas y valores.
 
        # Relacionar cada encabezado con su valor.
        for indice, encabezado in enumerate(encabezados):
            if encabezado != "":
                registro[encabezado] = fila[indice]
 
        registros.append(registro)
 
    return registros
 
 
def cargar_configuracion(ruta_archivo=None):
    """
    Abre el Excel, comprueba sus hojas y devuelve
    los parámetros y catálogos del proyecto.
    """
 
    
    if ruta_archivo is None: # Si no se proporciona una ruta (None), usar el Excel predeterminado del proyecto.
        ruta_archivo = (
            RUTA_PROYECTO / "config" / "parametros.xlsx"
        )
 
    libro = None
    try:
        # Comprobar que el archivo exista.
        if not ruta_archivo.exists():
            raise ErrorConfiguracion(
                f"No se encontró el archivo: {ruta_archivo}"
            )
 
        # load_workbook abre el Excel y devuelve un objeto para acceder a sus hojas;
        libro = load_workbook(
            ruta_archivo,
            data_only=True,
            read_only=True
        )
 
        # Comprobar que estén todas las hojas requeridas.
        for nombre_hoja in HOJAS_REQUERIDAS:
            if nombre_hoja not in libro.sheetnames:
                raise ErrorConfiguracion(
                    f"Falta la hoja '{nombre_hoja}' en el Excel."
                )
 
        # Leer los parámetros generales.
        parametros_lista = leer_tabla(
            libro["Parametros"],
            ["clave", "valor", "descripcion"]
        )
 
        parametros = {}
 
        for fila in parametros_lista:
            clave = fila["clave"]
 
            if clave is None or str(clave).strip() == "": # Se rechaza si no hay valor o si, al quitar espacios, la clave queda vacía.
                raise ErrorConfiguracion(
                    "Hay un parámetro sin clave."
                )
 
            clave = str(clave).strip()
 
            if clave in parametros: # Si la clave ya existe en parametros, se informa que está repetida.
                raise ErrorConfiguracion(
                    f"El parámetro '{clave}' está repetido."
                )
 
            parametros[clave] = fila["valor"]
 
        # Comprobar los parámetros que necesitamos.
        parametros_requeridos = [
            "dominio_correo",
            "archivo_salida",
            "prefijo_log",
            "formato_fecha_salida",
            "dias_maximo_futuro",
            "longitud_telefono",
            "nivel_log_minimo"
        ]
 
        for clave in parametros_requeridos:
            if clave not in parametros:
                raise ErrorConfiguracion(
                    f"Falta el parámetro obligatorio '{clave}'."
                )
 
            if parametros[clave] is None:
                raise ErrorConfiguracion(
                    f"El parámetro '{clave}' no tiene valor."
                )
 
        # Convertir los parámetros numéricos.
        try:
            parametros["dias_maximo_futuro"] = int(
                parametros["dias_maximo_futuro"]
            )
 
            parametros["longitud_telefono"] = int(
                parametros["longitud_telefono"]
            )
 
        except (ValueError, TypeError):
            raise ErrorConfiguracion(
                "Los días máximos y la longitud del teléfono deben ser números enteros."
            )
 
        # Leer el archivo de cargos.
        cargos = leer_tabla(
            libro["cargos"],
            ["codigo_cargo", "nombre_cargo", "nivel", "area"]
        )
 
        # Leer el archivo de centros de costo.
        centros_costo = leer_tabla(
            libro["centros_costo"],
            ["codigo", "nombre", "area"]
        )
 
        # Leer la matriz de permisos y perfiles.
        matriz_roles = leer_tabla(
            libro["matriz_roles"],
            [
                "codigo_cargo",
                "area",
                "perfil_sistema",
                "requiere_aprobacion"
            ]
        )
 
        # Leer los campos obligatorios por tipo de novedad.
        campos_requeridos = leer_tabla(
            libro["campos_requeridos"],
            ["tipo_novedad", "campos_requeridos"]
        )
 
        # Preparar todos los datos para los otros módulos.
        configuracion = {
            "parametros": parametros,
            "cargos": cargos,
            "centros_costo": centros_costo,
            "matriz_roles": matriz_roles,
            "campos_requeridos": campos_requeridos
        }
 
        return configuracion
 
    except ErrorConfiguracion:
        # Si el error ya es nuestro, lo dejamos pasar.
        raise
 
    except Exception as error:
        # Convertir otros errores de lectura en un error conocido.
        raise ErrorConfiguracion(
            f"No fue posible leer la configuración: {error}"
        ) from error
 
    finally:
        # Cerrar el Excel cuando terminemos de usarlo.
        if libro is not None:
            libro.close()