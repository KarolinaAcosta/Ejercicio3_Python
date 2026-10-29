#Se definen las clases con los errores posibles en el proyecto

class ErrorProyecto(Exception):
    """Error general del proyecto; sirve como clase base."""
    pass
 
 
class ErrorConfiguracion(ErrorProyecto):
    """Error al leer o validar el Excel de parámetros.
    Se lanza en modulos/configuracion.py.
    """
    pass
 
 
class ErrorArchivoEntrada(ErrorProyecto):
    """Error al buscar o leer el archivo JSON.
    Se lanza en modulos/lectura.py.
    """
    pass
 
 
class RegistroInvalido(ErrorProyecto):
    """Error cuando una novedad no cumple las validaciones.
    Se usa en modulos/procesamiento.py; el registro queda rechazado
    y el procesamiento continúa con la siguiente novedad.
    """
    pass
 
 
class ErrorReglaNegocio(ErrorProyecto):
    """Error al aplicar las reglas del negocio.
    Se usa en modulos/procesamiento.py para rechazar novedades que
    incumplen las reglas de área o la matriz de roles.
    """
    pass
 
 
class ErrorEscritura(ErrorProyecto):
    """Error al guardar los archivos de salida.
    Se lanza en modulos/reporte.py y modulos/registro.py.
    """
    pass