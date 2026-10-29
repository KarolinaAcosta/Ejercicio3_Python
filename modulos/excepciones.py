#Se definen las clases con los errores posibles en el proyecto

class ErrorProyecto(Exception):
    "Error general del proyecto."
    pass
 
 
class ErrorConfiguracion(ErrorProyecto):
    "Error al leer o validar el Excel de parámetros."
    pass
 
 
class ErrorArchivoEntrada(ErrorProyecto):
    "Error al buscar o leer el archivo JSON."
    pass
 
 
class RegistroInvalido(ErrorProyecto):
    "Error cuando una novedad no cumple las validaciones."
    pass
 
 
class ErrorReglaNegocio(ErrorProyecto):
    "Error al aplicar las reglas del negocio."
    pass
 
 
class ErrorEscritura(ErrorProyecto):
    "Error al guardar los archivos de salida."
    pass