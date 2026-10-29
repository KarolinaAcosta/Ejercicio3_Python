# SISTEMA PARA CONTROL DE REGISTRO MASIVO

## DESCRIPCION DEL SISTEMA

Este proyecto, se comprende de leer y validar la información en una base en archivo JSON, donde
el programa busca identificar especialmente los registros validos e incorrectas para generar
un reporte final, con las novedades y sus errores, validos o no.

## FUNCIONES

Contiene las siguientes funciones principales
1. Leer Archivo de Excel, para validar las hojas compuestas
2. Abrir y comprobar el archivo Excel, para devolver los parámetros del proyecto
3. Leer las novedades puestas en el archivo JSON
4. Procesar cada novedad y discernirla en aceptada, rechazada y brindar la colisión de los correos
5. Generación de correos para aquellas novedades que tenga prioridad ALTA
6. Creación de reporte con las novedades rechazadas, aceptadas y los correos correspondientes

## QUE ARCHIVOS CONFORMAN EL PROYECTO

El proyecto cuenta con 5 carpetas:
Carpeta Config: cuenta con el archivo "parametros.xlsx", donde se encuentras las reglas de negocio, 
cargos, centros de costos de la empresa, los cuales se manejan como linea base y reglas que debe seguir
el programa.

Carpeta Entrada: Cuenta con el archivo "novedades.JSON", Donde se presentan las ultimas novedades registradas
de la empresa, en el presente archivo cuenta con 19 novedades, varias de estas mismas las cuales cuentan con
errores para validación del programa.

Carpeta logs: La presente carpeta contiene el archivo "log_ejecucion.xlsx" donde muestra el día de ejecución del programa.

Carpeta Módulos: Contiene 7 archivos:
"configuracion.py": Se encarga de leer el archivo de parametros para poder identificar las columnas y filas del archivo
adicionalmente, cuenta con la configuración para mandar los errores si el archivo correspondiente de parámetros no tiene
los datos correspondientes.
"excepciones.py": Cuenta con las clases donde se colocan el tipo de excepciones para cada caso dentro del proyecto.
"lectura.py": Se encarga de leer el archivo JSON Con las novedades presentadas para la ejecucion del proyecto
"procesamiento.py": Se encarga del proceso interno y parte del proceso externo, donde se ejecutan las novedades, se validan
cada una para verificar si cumplen con los requisitos correspondientes y dado el caso se envia mensaje de error para seguir
con la ejecución. 
"registro.py":Registra los eventos del programa con fecha, nivel y mensaje y al finalizar, guarda esos registros y un resumen en
"reporte.py":genera un archivo Excel con las novedades aceptadas, rechazadas y las colisiones de correo.
"validacion.py": Revisa que cada novedad tenga los datos requeridos y que sus valores sean válidos, comprueba documentos,
centro de costo, fecha, teléfono y cargo; devuelve una lista con los errores encontrados.

Carpeta Salida: Cuenta con el reporte final de las novedades validas, rechazadas y el porqué de su rechazo

Archivo main.py: Coordina los módulos: carga la configuración y las novedades, procesa los registros, crea el reporte
y guarda los eventos de ejecución.

## ¿COMO EJECUTARLO?

Desde la carpeta principal del proyecto, abre una terminal y ejecuta python main.py. Lee la configuración de Excel
y las novedades JSON, y genera el reporte y el registro.
Este mismo procesara, ejecuciones.txt y generara un archivo llamado reporte.txt
