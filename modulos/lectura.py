import json
from pathlib import Path
 
 
def leer_novedades():
    carpeta = Path("entrada")
 
    # Buscar archivos JSON
    archivos = list(carpeta.glob("novedades_*.json"))
 
    if not archivos:
        raise FileNotFoundError("No hay archivos JSON en entrada.")
 
    # Elegir el archivo con la fecha más reciente en su nombre
    archivo = sorted(archivos)[-1]
 
    try: # try intenta leer el archivo; si el JSON está mal formado, except captura el error.
        with open(archivo, "r", encoding="utf-8") as documento:
            datos = json.load(documento)
 
    except json.JSONDecodeError:  
        raise ValueError("El archivo JSON tiene errores de formato.")
 
    # Comprobar la estructura principal
    if not isinstance(datos, dict) or "novedades" not in datos: # isinstance(datos, dict) comprueba que datos sea un diccionario.
        raise ValueError("El JSON debe contener la lista novedades.")
 
    if not isinstance(datos["novedades"], list): # Comprueba que el valor de "novedades" sea una lista.
        raise ValueError("novedades debe ser una lista.")
 
    return datos, archivo.name  # Devuelve el contenido del JSON y el nombre del archivo leído.