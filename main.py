from modulos.configuracion import cargar_configuracion
from modulos.lectura import leer_novedades
from modulos.procesamiento import procesar_novedades
from modulos.reporte import crear_reporte
from modulos.registro import registrar, guardar_registro
 
 
def main():
    try:
        registrar("Inicio del programa")
 
        configuracion = cargar_configuracion()
        print("TIPO;",type(configuracion["campos_requeridos"]))
        print("CONTENIDO"),
        repr(configuracion["campos_requeridos"])
        datos, nombre_archivo = leer_novedades()
 
        aceptados, rechazados, colisiones = procesar_novedades(
            datos, configuracion
        )
 
        ruta = crear_reporte(aceptados, rechazados, colisiones)
 
        registrar("Reporte creado: " + str(ruta))
 
        print("Archivo procesado:", nombre_archivo)
        print("Novedades recibidas:", len(datos["novedades"]))
        print("Aceptadas:", len(aceptados))
        print("Rechazadas:", len(rechazados))
        print("Colisiones de correo:", len(colisiones))
        print("Reporte guardado en:", ruta)
 
    except Exception as error:
        registrar("Error: " + str(error), "ERROR")
        print("Ocurrio un error:", error)
 
    finally:
        guardar_registro()
 
 
if __name__ == "__main__":
    main()