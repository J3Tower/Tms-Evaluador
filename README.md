
FUNCIONALIDAD:
Analiza particiones NTFS en busca de indicios sobre la manipulación de sellos temporales de los archivos, generando un timeline alternativo mostrando las incoherencias detectadas.


REQUISITOS:
Disponer de un entorno Windows para la ejecución
Instalación del software:
	1.- Python 2.7.11 Descarga en https://www.python.org/download/releases/2.7.11

	2.- SleuthKit para Windows. En descarga de https://github.com/sleuthkit/sleuthkit/releases/download/sleuthkit-4.3.0/sleuthkit-4.3.0-win32.zip

	3.- Parsers NTFS: Mft2Csv, UsnJrnl2Csv, LogFileParser. En descarga de https://github.com/jschicht/
	
	4.- Actualización sqlite3 para python 2.7 en Windows. Descarga en https://www.sqlite.org/2016/sqlite-dll-win32-x86-3150100.zip.

Sleuthkit y los parsers deberán ser instalarse en un mismo directorio accesible localmente

IMAGEN A ANALIZAR:
Disponer de imagen RAW de partición en formato NTFS

USO:
tms-evaluador.py -i <fichero-imagen>  -o <fichero-salida> -p <ruta-parsers>
Ejemplo: tms-evaluador.py -i  img.dd -o salida -p parsers



