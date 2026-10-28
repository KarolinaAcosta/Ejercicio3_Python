from openpyxl import Workbook
from pathlib import Path
from datetime import datetime
 
 
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
    Path("logs").mkdir(exist_ok=True)
 
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
    libro.save(ruta)
    libro.close()
 
    return ruta