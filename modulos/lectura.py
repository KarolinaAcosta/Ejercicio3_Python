import json
from pathlib import Path

from modulos.excepciones import ErrorArchivoEntrada


def leer_novedades():
    carpeta = Path("entrada")
 
    # Buscar archivos JSON
    archivos = list(carpeta.glob("novedades_*.json"))
 
    if not archivos:
        raise ErrorArchivoEntrada("No hay archivos JSON en entrada.")
 
    # Elegir el archivo con la fecha más reciente en su nombre
    archivo = sorted(archivos)[-1]
 
    try:
        with open(archivo, "r", encoding="utf-8") as documento:
            datos = json.load(documento)
    except json.JSONDecodeError as error:
        raise ErrorArchivoEntrada(
            "El archivo JSON tiene errores de formato."
        ) from error
    except (OSError, UnicodeDecodeError) as error:
        raise ErrorArchivoEntrada(
            f"No fue posible leer el archivo JSON: {error}"
        ) from error

    # Comprobar la estructura principal
    if not isinstance(datos, dict) or "novedades" not in datos:
        raise ErrorArchivoEntrada(
            "El JSON debe contener la lista novedades."
        )

    if not isinstance(datos["novedades"], list):
        raise ErrorArchivoEntrada("novedades debe ser una lista.")

    return datos, archivo.name