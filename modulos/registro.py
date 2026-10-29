from openpyxl import Workbook
from pathlib import Path
from datetime import datetime

from modulos.excepciones import ErrorEscritura
 
 
eventos = []
 
 
def registrar(mensaje, nivel="INFO"):
    # Guardar un evento en la lista
    evento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nivel": nivel,
        "mensaje": mensaje
    }
 
    eventos.append(evento)
 
 
def guardar_registro():
    # Crear la carpeta de registros si no existe
    try:
        Path("logs").mkdir(exist_ok=True)
    except OSError as error:
        raise ErrorEscritura(
            f"No fue posible crear la carpeta de registros: {error}"
        ) from error
 
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Detalle"
 
    hoja.append(["Fecha", "Nivel", "Mensaje"])
 
    for evento in eventos:
        hoja.append([
            evento["fecha"],
            evento["nivel"],
            evento["mensaje"]
        ])
 
    # Crear una hoja con el resumen
    resumen = libro.create_sheet("Resumen")
    resumen.append(["Concepto", "Cantidad"])
    resumen.append(["Total de eventos", len(eventos)])
 
    ruta = Path("logs/log_ejecucion.xlsx")
    try:
        libro.save(ruta)
    except Exception as error:
        raise ErrorEscritura(
            f"No fue posible guardar el registro: {error}"
        ) from error
    finally:
        libro.close()

    return ruta