# TMS-EVALUADOR.py
Herramienta para el análisis de particiones NTFS en busca de indicios sobre la manipulación de sellos temporales de los archivos, generando un timeline alternativo mostrando las incoherencias detectadas.
### ENTORNO:
Requiere un entorno Windows para su ejecución
### INSTALACIÓN
* Descarga de [Python 2.7.11](https://www.python.org/download/releases/2.7.11)
* Descarga de [SleuthKit para Windows](https://github.com/sleuthkit/sleuthkit/releases/download/sleuthkit-4.3.0/sleuthkit-4.3.0-win32.zip)
* Descarga de parsers NTFS: [Mft2Csv](https://github.com/jschicht/Mft2Csv), [UsnJrnl2Csv](https://github.com/jschicht/UsnJrnl2Csv), [LogFileParser](https://github.com/jschicht/LogFileParser).
* Actualización [Sqlite3 para python 2.7 en Windows](https://www.sqlite.org/2016/sqlite-dll-win32-x86-3150100.zip).

Sleuthkit y los parsers deberán ser instalarse en un mismo directorio accesible localmente
### ELEMENTO DE ANÁLISIS:
Imagen RAW de un volumen NTFS
### USO:
$ tms-evaluador.py -i <imagen>  -o <fichero-CSV-salida> -p <ruta-parsers>

Ejemplo: $ tms-evaluador.py -i  img.dd -o salida -p parsers

### LICENCIA:
Open Source

### Proyecto
En el marco del TFM Unir sobre la Detección Antiforense Open Source.

Autor: Jose B Torres.
