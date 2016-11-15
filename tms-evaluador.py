#!/usr/bin/python

import sys, os, getopt, sqlite3, fnmatch, csv, subprocess, time

DEBUG_STATUS = False #Activa o desactiva los mensajes de depuración

"""Constantes de configuración"""
TAG = u"" #Se sustituye por self.params.tag
TMPDIR = u".\\TMP" 
FCAT_PATH = u""
BD_FULLNAME = u".\\tms-eval.db"
PROJ_PATH = u"" + os.getcwd()
FULLPATH_TMPDIR = PROJ_PATH + TMPDIR[1:]

"""Constantes para los artefactos"""
LOGFILE = u"$LogFile"
MFT		= u"$MFT"
USNJRNL	= u"$J"
I30	= u"$I30"

class debug():

	def __init__(self,activado):
		if activado: print(u"\n\n ***ERROR***:\n línea: %s.\t Proc: %s\t msg: %s\n\n" % ((sys._getframe(2).f_lineno),( sys._getframe().f_code.co_name), sys.exc_info()[:2]))
		
		
class Progress():

	def __init__(self, msg, barLength):
	
		self.msg = msg
		self.barLenght = barLength
	
	def update_progress(self, progress):
		
		status = " "
		
		if isinstance(progress, int):
			progress = float(progress)
		
		if progress >= 1:
			progress = 1
			status = "...Hecho \r\n\n"
			
		block = int(round(self.barLenght*progress))
		text = "\r" + self.msg + ": [{0}] {1}% {2}".format( "#"*block + "-"*(self.barLenght-block), progress*100, status)
		sys.stdout.write(text)
		sys.stdout.flush()
		
		return ""
		
class FileBase():
		
	def ExecuteHideStdOut(self, cmdlist):
		try:
			FNULL = open(os.devnull, 'w')
			retcode = subprocess.call(cmdlist, stdout=FNULL, stderr=subprocess.STDOUT)
			FNULL.close()
		except:
			return 0
		
	def Is64Windows(self):
		return 'PROGRAMFILES(X86)' in os.environ
		
	def FindLastDir(self,dirbase, patron):
		for dir in os.listdir(dirbase):
			try:
				if fnmatch.fnmatch(dir, patron):
					return dir
			except:
				return ""
				
	def ReadBinaryFile(self,fichero):
	
		size = os.stat(fichero).st_size
		try:
			in_file = open(fichero, "rb") 
			contenido  = in_file.read(size) 
			in_file.close() 
			
			return contenido
		except:
			print("Error no tratado en llamada:", sys.exc_info()[:2])
			return []
			
	def WriteBinaryFile(self,fichero,contenido):
		try:
			out_file = open(fichero, "wb") 
			out_file.write(contenido) 
			out_file.close() 
			return 1
		except:
			return 0
				
	def ReadFile(self,fichero):
		try:
			in_file = open(fichero, "rt") 
			contenido  = in_file.read() 
			in_file.close() 
			
			return contenido
		except:
			return ""
			
	def WriteFile(self,fichero,contenido):
		try:
			out_file = open(fichero, "wt") 
			out_file.write(contenido) 
			out_file.close() 
			return 1
		except:
			return 0
			
	def GetLastFileOutputDIR(self, path, patron):
		dic = {}
		
		for f in os.listdir(path):
			if fnmatch.fnmatch(f, patron):
				dic[f]=os.stat(path+"\\"+f).st_mtime
				
		return list(sorted(dic,reverse=True))[0]
		
	def GetPathMatch(self, dirbase, FileName):
		try:
			for root, dirs, files in os.walk(dirbase):
				for file in files:
					if fnmatch.fnmatch(file, FileName):
						return root + u"\\" + FileName
		except:
			return ""
			
	def DeleteFolder(self, dirbase):
		try:
			for root, dirs, files in os.walk(dirbase, topdown=False):
				for name in files:
					os.remove(os.path.join(root, name))
				for name in dirs:
					os.rmdir(os.path.join(root, name))
					
			os.rmdir(root)
		except:
			return ""
	
class Detector():

	def __init__(self,cnn):
		self.cnn = cnn
		
		self.TimeLineInferido = ""
		self.SQL = ""
		self.SQL_List = []
		self.ltag = ""
		self.params = ""
				
	def __CreaTablaTimeLine(self):
		
		try:
			self.cnn.Execute("Drop table if exists timeline")
		except:
			debug(DEBUG_STATUS)
		
		try:
			self.cnn.Execute("Drop table if exists resultados")
		except:
			debug(DEBUG_STATUS)
			
		try:
			self.cnn.Execute(u"CREATE TABLE timeline AS SELECT * FROM " + TAG + "MFT2CSV")
			
			self.cnn.Execute(u"update timeline set SI_CTime=substr(SI_CTime,7,4) || '-' || substr(SI_CTime,4,2)  || '-' || " + \
			"substr(SI_CTime,1,2) || ' ' || substr(SI_CTime,12, length(SI_CTime)-11)") 
			
			self.cnn.Execute(u"update timeline set SI_ATime=substr(SI_ATime,7,4) || '-' || substr(SI_ATime,4,2)  || '-' || " + \
			"substr(SI_ATime,1,2) || ' ' || substr(SI_ATime,12, length(SI_ATime)-11)")  
			
			self.cnn.Execute(u"update timeline set SI_MTime=substr(SI_MTime,7,4) || '-' || substr(SI_MTime,4,2)  || '-' || " + \
			"substr(SI_MTime,1,2) || ' ' || substr(SI_MTime,12, length(SI_MTime)-11)") 
			
			self.cnn.Execute(u"update timeline set SI_RTime=substr(SI_RTime,7,4) || '-' || substr(SI_RTime,4,2)  || '-' || " + \
			"substr(SI_RTime,1,2) || ' ' || substr(SI_RTime,12, length(SI_RTime)-11)")
			
			self.cnn.Execute(u"update timeline set FN_CTime=substr(FN_CTime,7,4) || '-' || substr(FN_CTime,4,2)  || '-' || " + \
			"substr(FN_CTime,1,2) || ' ' || substr(FN_CTime,12, length(FN_CTime)-11)")
			
			self.cnn.Execute(u"update timeline set FN_ATime=substr(FN_ATime,7,4) || '-' || substr(FN_ATime,4,2)  || '-' || " + \
			"substr(FN_ATime,1,2) || ' ' || substr(FN_ATime,12, length(FN_ATime)-11)")
			
			self.cnn.Execute(u"update timeline set FN_MTime=substr(FN_MTime,7,4) || '-' || substr(FN_MTime,4,2)  || '-' || " + \
			"substr(FN_MTime,1,2) || ' ' || substr(FN_MTime,12, length(FN_MTime)-11)")
			
			self.cnn.Execute(u"update timeline set FN_RTime=substr(FN_RTime,7,4) || '-' || substr(FN_RTime,4,2)  || '-' || " + \
			"substr(FN_RTime,1,2) || ' ' || substr(FN_RTime,12, length(FN_RTime)-11)")
			
			
			self.SQL = 	u"WITH RECURSIVE mft AS (select timeline.Header_MFTRecordNumber RecordNo, timeline.Header_SequenceNo SequenceNo, " + \
						"timeline.FN_ParentReferenceNo, timeline.FN_ParentSequenceNo, " + \
						"timeline.FN_FileName from timeline where Header_MFTRecordNumber='5' " + \
						"union select mft2.Header_MFTRecordNumber, mft2.Header_SequenceNo, mft2.FN_ParentReferenceNo, mft2.FN_ParentSequenceNo,  " + \
						"mft.FN_Filename || '\\' || mft2.FN_FileName FN_FileName  " + \
						"from timeline mft2 inner join mft on mft2.FN_ParentReferenceNo=mft.RecordNo and mft2.FN_ParentSequenceNo=mft.SequenceNo where mft2.Header_MFTRecordNumber<>'5') " + \
						"select * from mft "
			
			try:
				
				cur = self.cnn.GetCursor(self.SQL)
				cur2 = self.cnn.Cursor()
				
				if not (cur is None):
					cols = cur.fetchone()
										
					while not (cols is None):
						self.SQL = u"update timeline set filepath='" + cols[4] + "' where HEADER_MFTREcordNumber='" + \
						cols[0] + "' and HEADER_SequenceNo='" + cols[1] + "' "
						try:
							cur2.execute(u"" + self.SQL)
							cols = cur.fetchone()
						except:
							return None
							
					cur2.close()
					cur.close()	
				else:
					print(u"No funciona el cursor recursivo")
					return None
			except:
				debug(DEBUG_STATUS)
				return None
		except:
			debug(DEBUG_STATUS)
			return None
	
		try:
			self.SQL = "Select * from timeline "
			return  self.cnn.GetCursor(self.SQL)
		except:
			return None
			
	
	def __SqlUpd_Validacion_MFT(self):
		#Sensibilidad: MEDIA
		#Confiabilidad: ALTA
		#POSITIVO SI: El Creation time de $SI es anterior al de $FN
		SQL = "(select CASE WHEN resultados.jtime=julianday(FN_CTime) and resultados.FN='1' THEN '' ELSE " + \
		"substr(FN_CTime,9,2) || '/' || substr(FN_CTime,6,2)  || '/' || substr(FN_CTime,1,4) || ' ' || substr(FN_CTime,12, length(FN_CTime)-11) END SuspectedTMS " + \
		"from timeline where (julianday(SI_CTime)<>julianday(FN_CTime)) and timeline.RecordOffset=resultados.RecordOffset " + \
		"and (instr(resultados.TMS,'B')>0) )"
		
		return "update resultados set TMSChecked='1', mft_suspectedct=" + SQL + "where exists " + SQL
	
	def __SqlUpd_Validacion_MFT_USN(self):
		#Sensibilidad: MEDIA
		#Confiabilidad: MEDIA ... Se basa en al último USN registrado por la entrada y existe una operación sospechosa
		#POSITIVO SI: El usn de la entrada MFT apunta a una reason BASIC_INFO_CHANGE+CLOSE
		SQL = u"update " + TAG + "usnjrnl set [Timestamp]=substr([Timestamp],7,4) || '-' || substr([Timestamp],4,2)  || '-' || substr([Timestamp],1,2) || ' ' || substr([Timestamp],12, length([Timestamp])-11) where instr([Timestamp],'/')>0 "
			
		self.cnn.Execute(SQL)
		
		SQL = u"(select CASE WHEN resultados.jtime=julianday(usn.[Timestamp]) and resultados.FN='1' THEN '' ELSE " + \
		" 'BASIC_INFO_CHANGE+CLOSE' END SuspectedTMS " + \
		"from timeline timeline " + \
		"inner join " + TAG + "usnjrnl usn  on timeline.SI_USN=usn.usn " + \
		"where usn.reason='BASIC_INFO_CHANGE+CLOSE' " + \
		"and timeline.RecordOffset=resultados.RecordOffset and resultados.FN='0' and (instr(resultados.TMS,'B')>0)) "
	
		return "update resultados set TMSChecked='1', MFT_USN_SuspectedCT=" + SQL + "where exists " + SQL
			
	def __SqlUpd_Validacion_MFT_USN_LOG(self):
		#Sensibilidad: ALTA
		#Confiabilidad: BAJA
		#POSITIVO SI: Cuando usando log de  usn,  la entrada MFT apunta a una reason BASIC_INFO_CHANGE+CLOSE cruzando con 
		#             MFT.MFTReference y Filename
		SQL = u"(select CASE WHEN resultados.FN='1' THEN '' ELSE 'BASIC_INFO_CHANGE+CLOSE' END SuspectedTMS " + \
		"from timeline timeline " + \
		"inner join " + TAG + "logfile_lfusnjrnl usn on usn.MFTReference=timeline.HEADER_MFTRecordNumber and usn.FileName=timeline.FN_FileName " + \
		"where usn.reason='BASIC_INFO_CHANGE+CLOSE' " + \
		"and timeline.RecordOffset=resultados.RecordOffset and resultados.FN='0' and (instr(resultados.TMS,'B')>0)) "
		
		return "update resultados set TMSChecked='1', MFT_USN_LOG_SuspectedCT=" + SQL + "where exists " + SQL
	
	def __SqlUpd_Validacion_MFT_LOG_IDX(self):
		#Sensibilidad: MEDIA... Comprueba tanto $SI como $FN en relación con que el TMS de Creación de $SI 
		#			   en el log, haya sido en algún momento posterior al de creación que figura en MFT.SI_CTime
		#Confiabilidad: ALTA
		#POSITIVO SI: El $SI_CTime es anterior al CTime en el log de atributos índice, cruzando por entrada MFT
		#             y Número de secuencia 
		SQLInterior = "select timeline.RecordOffset,logs.TMS_Ref  SuspectedCT " + \
						"from timeline  " + \
						"inner join " + \
							"(select lfI30.lf_MFTReference MFTRecordNo , lfI30.lf_MFTReferenceSeqNo MFTRecordSeqNo, " + \
								"substr(lf_CTime,7,4) || '-' || substr(lf_CTime,4,2)  || '-' || substr(lf_CTime,1,2) " + \
								"|| ' ' || substr(lf_CTime,12, length(lf_CTime)-11) TMS_Ref " + \
								"from " + TAG + "LogFile_INDX_I30 lfI30 " + \
						") logs on  logs.MFTRecordNo=timeline.HEADER_MFTRecordNumber and logs.MFTRecordSeqNo=timeline.Header_SequenceNo " + \
						"Where ((timeline.RecordOffset=resultados.RecordOffset) and (instr(resultados.TMS,'B')>0)) " + \
						" and (((resultados.FN='0') and (julianday(timeline.SI_CTime)<julianday(logs.TMS_Ref))) )"
		
		SQL = "(select " + \
		"substr(SuspectedCT,9,2) || '/' || substr(SuspectedCT,6,2)  || '/' || substr(SuspectedCT,1,4) || ' ' || " + \
		"substr(SuspectedCT,12, length(SuspectedCT)-11) SuspectedTMS " + \
		"from ( " + SQLInterior + " ) K where K.RecordOffset=resultados.RecordOffset and (instr(resultados.TMS,'B')>0)) "
		
		return "update resultados set TMSChecked='1', MFT_LOG_IDX_SuspectedCT=" + SQL + "where exists " + SQL
		

	def __GetFullPathMftEntry(self):
		
		cur = self.cnn.GetCursor(u"select Header_MFTRecordNumber RecordNo, Header_SequenceNo SequenceNo, " + \
		"FN_ParentReferenceNo, FN_ParentSequenceNo, " + \
		"FN_FileName from " + TAG + "mft2csv mft where Header_MFTRecordNumber='5' ")
								
		cols = cur.fetchone()
		secuencia=[]
		
		while not (cols is None):
			RecordNo = cols['RecordNo']
			SequenceNo = cols['SequenceNo']
			Filename = cols['FN_FileName']
			
			secuencia.append(cols)
			
			SQL = u"select mft2.Header_MFTRecordNumber, mft2.Header_SequenceNo, mft2.FN_ParentReferenceNo, " + \
			"mft2.FN_ParentSequenceNo, '" + Filename + "' || '\\' || mft2.FN_FileName FN_FileName " + \
			"from " + TAG + "mft2csv mft2 where mft2.FN_ParentReferenceNo='" + RecordNo + "' " + \
			"and mft2.FN_ParentSequenceNo='" + SequenceNo + "' where mft2.Header_MFTRecordNumber<>'5'"
			
			cur.execute(SQL)
			cols = cur.fetchone()
			
		cur.close()	
		return secuencia
		
	def __GetSecuencia(self, lsn_inicio):
	
		cur = self.cnn.GetCursor(u"select lf_lsn from " + TAG + "LogFile where lf_lsn='" + lsn_inicio + \
		"' and lf_lsnprevious='0' ")
				
		cols = cur.fetchone()
		secuencia=[]
		
		while not (cols is None):
			lsn = cols[0]
			secuencia.append(lsn)
			cur.execute(u"select lf_lsn from " + TAG + "LogFile where lf_lsnprevious='"  + lsn + "'")
			cols = cur.fetchone()
			
		cur.close()	
		return secuencia
		
	def __CreaResultados(self,params):
		""" Exporta en CSV """
				
		SQL = u"create table resultados as " + \
				"select pivote.jTime, tl.RecordOffset, " + \
				"	substr(pivote.dTime,9,2) || '/' || substr(pivote.dTime,6,2)  || '/' || substr(pivote.dTime,1,4) || ' ' || " + \
				"   substr(pivote.dTime,12, length(pivote.dTime)-11) TMS_Ref, " + \
				"	CASE WHEN tl.mSI_MTime=pivote.dTime THEN 'M' ELSE '.' END || " + \
				"   CASE WHEN tl.mSI_ATime=pivote.dTime THEN 'A' ELSE '.' END || " + \
				"	CASE WHEN tl.mSI_CTime=pivote.dTime THEN 'C' ELSE '.' END || " + \
				"   CASE WHEN tl.mSI_BTime=pivote.dTime THEN 'B' ELSE '.' END TMS, " + \
				"	'0' FN, tl.FilePath Filename, " + \
				"	CASE WHEN tl.RecordActive='ALLOCATED' THEN '' ELSE '(Eliminado)' END status,  " + \
				"	CASE WHEN tl.Header_Flags='FOLDER' THEN 'directorio' ELSE 'archivo' END tipoarch, " + \
				"	tl.Header_MFTRecordNumber RecordNo, tl.Header_SequenceNo SequenceNo, " + \
				"   '' TMSChecked, '' TMS_Msg, '' MFT_SuspectedCT, '' MFT_USN_SuspectedCT, '' MFT_USN_LOG_SuspectedCT, " + \
				"    '' MFT_LOG_IDX_SuspectedCT " + \
				"from  " + \
				"(  " + \
				"   select distinct jTime, dTime " + \
				"   from " + \
				"   (select julianday(SI_CTime) jTime, SI_CTime dTime from timeline " + \
				"    union select julianday(SI_MTime), SI_MTime from timeline " + \
				"    union select julianday(SI_ATime), SI_ATime from timeline " + \
				"    union select julianday(SI_RTime), SI_RTime from timeline) jLista " + \
				"    order by 1 asc" + \
				") pivote " + \
				"inner join " + \
				"( " + \
				"   select  RecordOffset, SI_CTime mSI_BTime,SI_MTime mSI_MTime,  SI_ATime mSI_ATime, SI_RTime mSI_CTime, " + \
				"           FN_Filename, Header_MFTRecordNumber, Header_SequenceNo, RecordActive,Header_Flags, FilePath " + \
				"   from timeline  " + \
				"   order by 1, 2, 3, 4 " + \
				") tl  on (pivote.dTime=mSI_BTime or pivote.dTime=mSI_MTime or pivote.dTime=mSI_ATime or pivote.dTime=mSI_CTime) " + \
				"where pivote.jtime is not null "
				
		SQL = SQL + "UNION " + \
				"select  " + \
				"	pivote.jTime ,tl.RecordOffset, " + \
				"	substr(pivote.dTime,9,2) || '/' || substr(pivote.dTime,6,2)  || '/' || substr(pivote.dTime,1,4) || ' ' || " + \
				"   substr(pivote.dTime,12, length(pivote.dTime)-11) TMS_Ref, " + \
				"	CASE WHEN tl.mFN_MTime=pivote.dTime THEN 'M' ELSE '.' END || " + \
				"	CASE WHEN tl.mFN_ATime=pivote.dTime THEN 'A' ELSE '.' END || " + \
				"	CASE WHEN tl.mFN_CTime=pivote.dTime THEN 'C' ELSE '.' END || " + \
				"   CASE WHEN tl.mFN_BTime=pivote.dTime THEN 'B' ELSE '.' END TMS, " + \
				"	'1' FN, tl.FilePath || ' ($FILE_NAME)' Filename, " + \
				"	CASE WHEN tl.RecordActive='ALLOCATED' THEN '' ELSE '(Eliminado)' END status,  " + \
				"	CASE WHEN tl.Header_Flags='FOLDER' THEN 'directorio' ELSE 'archivo' END tipoarch, " + \
				"	tl.Header_MFTRecordNumber RecordNo, tl.Header_SequenceNo SequenceNo,  " + \
				"   '' TMSChecked, '' TMS_Msg, '' MFT_SuspectedCT, '' MFT_USN_SuspectedCT, '' " + \
				"   MFT_USN_LOG_SuspectedCT, '' MFT_LOG_IDX_SuspectedCT " + \
				"from  " + \
				"( " + \
				"   select distinct jTime, dTime " + \
				"   from " + \
				"   ( " + \
				"       select julianday(FN_CTime) jTime, FN_CTime dTime from timeline " + \
				"       union select julianday(FN_MTime), FN_MTime  from timeline " + \
				"       union select julianday(FN_ATime), FN_ATime from timeline " + \
				"       union select julianday(FN_RTime) , FN_RTime from timeline " + \
				"    ) jLista " + \
				"    order by 1 asc " + \
				") pivote " + \
				"inner join  " + \
				"( " + \
				"   select  RecordOffset, FN_CTime mFN_BTime,FN_MTime mFN_MTime,  FN_ATime mFN_ATime, " + \
				"           FN_RTime mFN_CTime, FN_Filename,  Header_MFTRecordNumber, Header_SequenceNo, " + \
				"           RecordActive, Header_Flags, FilePath " + \
				"   from timeline  " + \
				"   order by 1, 2, 3, 4 " + \
				") tl  on (pivote.dTime=mFN_BTime or pivote.dTime=mFN_MTime " + \
				"               or pivote.dTime=mFN_ATime or pivote.dTime=mFN_CTime) " + \
				"where pivote.jtime is not null " + \
				"order by 1"
				
		self.cnn.Execute(SQL)
		
		if not self.cnn.Execute(self.__SqlUpd_Validacion_MFT()):  
			print("No se ejecutó el detector MFT")
		if not self.cnn.Execute(self.__SqlUpd_Validacion_MFT_USN()): 
			print("No se ejecutó el detector MFT_USN")
		if not self.cnn.Execute(self.__SqlUpd_Validacion_MFT_USN_LOG()): 
			print("No se ejecutó el detector MFT_USN_LOG")
		if not self.cnn.Execute(self.__SqlUpd_Validacion_MFT_LOG_IDX()): 
			print("No se ejecutó el detector MFT_LOG_IDX")
		
		
		SQL = u"select " + \
		"             RecordOffset,TMS_Ref TMS,TMS Meta,Filename Fichero,status,tipoarch Tipo,RecordNo " + \
		"             MFT_RecNo,SequenceNo MFT_SeqNo,TMS_Msg Evaluacion,MFT_SuspectedCT Infer_MFT," + \
		"             MFT_USN_SuspectedCT Infer_MFT_USN, MFT_USN_LOG_SuspectedCT Infer_MFT_USN_LOG, " + \
		"             MFT_LOG_IDX_SuspectedCT Infer_MFT_LOG_IDX " + \
		"       from resultados "
		
		return  Extractor().ExportaSQL2CSV(self.cnn, SQL, PROJ_PATH + "\\" + params.outputfile.replace(".csv","") + ".csv")		
		
	def Procesa(self,params):
		
		
		progreso_detector = Progress("Detectando", 3)
		
		Mft2Csv(cnn).Procesa(params)
		progreso_detector.update_progress(0.33)
		
		Usn2Csv(cnn).Procesa(params)
		progreso_detector.update_progress(0.66)
		
		LogFileParser(cnn).Procesa(params)
		progreso_detector.update_progress(1.0)
		
		self.curTL = self.__CreaTablaTimeLine()
				
		return self.__CreaResultados(params)
				
class Extractor(): #OK
	def __init__(self):
		return
		
	def Stdout2File(self, ficheroOut, paramList):
		try:
			out_file = open(ficheroOut, "wb") 
			process = subprocess.Popen(paramList, stdout=out_file)
			process.wait()
			out_file.close()
			process.terminate()
			process.kill()
			return 1
		except:
			print("Error no tratado en llamada a Stdout2File:", sys.exc_info()[:2])
			return 0
				
	def Extrae(self, inputfile, artefacto):

		if artefacto==MFT:
			sExtraccion = u"" + FCAT_PATH + " -f ntfs $MFT " + inputfile + " > " + TMPDIR + "\\" + MFT 
		elif artefacto==LOGFILE:
			sExtraccion = u"" + FCAT_PATH + " -f ntfs $LogFile " + inputfile + " > " + TMPDIR + "\\" + LOGFILE 
		elif artefacto==USNJRNL:
			sExtraccion = u"" + FCAT_PATH + " -f ntfs $Extend/$UsnJrnl:$J " + inputfile + " > " + TMPDIR + "\\" + USNJRNL 
		try:
			os.system(sExtraccion)
			return 1
		except:
			print(u"Error al extraer el artefacto " + artefacto)
			return 0
			
	def ExportaSQL2CSV(self, cnn, SQL, outputfile):
		
		try:
			cur = cnn.GetCursor(SQL)
			data = cur.fetchall()
		
			f = open(outputfile, 'wb')
			writer = csv.writer(f)
			writer.writerow([i[0] for i in cur.description]) # write headers
			writer.writerows(data)
		
			f.close()
			cur.close()
			return 1
		except:
			debug(DEBUG_STATUS)
			return 0
		
class Importador(): #OK

	def __init__(self,cnn):
		self.cnn = cnn
		
	def ImportaCSV(self,filenameCSV, tablename, delimitador, comillas):
		
		try:
			self.cnn.ExecuteSQL("Drop table if exists " + TAG + tablename)
		except:
			pass
		
		if (os.path.isfile(filenameCSV)):
			try:
				fichero = open(filenameCSV,'rb')
			except:
				debug(DEBUG_STATUS)
				return 0
		else:
			if (os.path.isfile(filenameCSV + u".empty")):
				try:
					fichero = open(filenameCSV + u".empty",'rb')
				except:
					debug(DEBUG_STATUS)
					return 0
			else:
				return 0
			
		outfile = open(filenameCSV + ".tmp", "w") 
		outfile.write(fichero.read().replace("\0", ""))
		outfile.close()
		fichero.close()
		
		fichero = open(filenameCSV + ".tmp",'rb')
		
		try:
			dr = csv.reader(fichero, delimiter=delimitador, quotechar=comillas)
			rownumber = 1
			for row in dr:
				valor = ""
				for col in row:
					valor += "'" + str(col).lstrip() + "',"
					to_db = valor[:len(valor)-1]

				if rownumber==1:
					nombre_columnas = str(to_db)
					sSQL = u"CREATE TABLE " + TAG + tablename + " (" + nombre_columnas + ");"
					
					self.cnn.ExecuteSQL(sSQL) 
				else:
					to_db = to_db.replace('"','')
					to_db = to_db.replace("'/'","")
					self.cnn.ExecuteSQL(u"INSERT INTO " + TAG + tablename + " (" + nombre_columnas + ") VALUES (" + str(to_db) + ");")
				rownumber += 1
			fichero.close()	
			return 1
		except:
			debug(DEBUG_STATUS)
			fichero.close()
			return 0
		
class LogFileParser(): #OK
	
	def __init__(self, cnn):
		self.cnn = cnn
		
		self.FilePath = u"."
		self.File64 = "LogFileParser64.exe"
		self.File32 = u"LogFileParser.exe"
		
		if FileBase().Is64Windows:
			self.FileType = "PE64"
			self.SourceIs32bit = 0 #1 indica origen SO de 32 bits. 
		else:
			self.SourceIs32bit = 1 #1 indica origen SO de 32 bits. 
			self.FileType = "PE32"
				
		self.MFTRecordSize = 1024
		self.SectorsPerCluster = 8
		
		self.LogFileOutputDIR = ""
		
		cwd = os.getcwd()
			
		cmdlineparams = u" /LogFileFile:" + FULLPATH_TMPDIR + "\\" + LOGFILE
		cmdlineparams = cmdlineparams + " /OutputPath:" + FULLPATH_TMPDIR
		cmdlineparams = cmdlineparams + " /TimeZone:0.00"
		cmdlineparams = cmdlineparams + " /OutputFormat:csv"
		cmdlineparams = cmdlineparams + " /BrokenMFT:1"
		cmdlineparams = cmdlineparams + " /TSFormat:3" #DD/MM/YY HH:MM:SS.NNNNNNN
		cmdlineparams = cmdlineparams + " /MFTRecordSize:" + str(self.MFTRecordSize)
		cmdlineparams = cmdlineparams + " /SectorsPerCluster:" + str(self.SectorsPerCluster)
		cmdlineparams = cmdlineparams + " /SourceIs32bit:" + str(self.SourceIs32bit)
		cmdlineparams = cmdlineparams + " /ExtractDataUpdates:1" #1 extracción del contenido residente
		cmdlineparams = cmdlineparams + " /ExtractDataUpdatesSize:20" #Tamaño en bytes del contenido residente a extraer
		cmdlineparams = cmdlineparams + " /SkipSqlite3:0" #0 genera los sql aparte de la base de datos.
			
		self.cmdlineparams = cmdlineparams
		
	def ImportaCSV(self):
		try:
			if len(self.LogFileOutputDIR)>0:
				if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile.csv", "LogFile", "|", "'"):
					if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile_TxfData.csv", "LogFile_TxfData", "|", "'"):
						if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile_lfUsnJrnl.csv", "LogFile_lfUsnJrnl", "|", "'"):
							if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile_INDX_I30.csv", "LogFile_INDX_I30", "|", "'"):
								if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile_AllTransactionHeaders.csv", "LogFile_AllTransHeaders", "|", "'"):
									if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + self.LogFileOutputDIR + "\\LogFile_UpdateFileName_I30.csv", "LogFile_UpdateFileName_I30", "|", "'"):
										return 1
									else:
										return 0
		except:
			debug(DEBUG_STATUS)
	
	def Procesa(self, params):
		
		if  Extractor().Extrae(params.inputfile, LOGFILE):
		
			if params.Win64: #Versión de parsers Windows de 64 bits
				self.File = self.File64
			else:
			    self.File = self.File32
				
			self.FilePath = FileBase().GetPathMatch(params.rutaparsers,self.File)
		
			if (len(self.FilePath)>0):
				try:
					stmp = self.FilePath + ' ' + self.cmdlineparams
					FileBase().ExecuteHideStdOut(stmp.split(" "))
					
					try:
						self.LogFileOutputDIR = FileBase().GetLastFileOutputDIR(FULLPATH_TMPDIR,'LogFile_2*')
						self.ImportaCSV()
						return 1
					except:
						print(u"ERROR importando CSV de LogFileParser\n")
						return 0
				except:
					debug(DEBUG_STATUS)
					print(u"ERROR procesando LogFileParser...\n")
					return 0
			else:
				return 0

class Usn2Csv(): #OK

	def __init__(self, cnn):
		self.cnn = cnn
		self.FilePath = u"."
		self.File = "UsnJrnl2Csv.exe"
		self.File64 = "UsnJrnl2Csv64.exe"
		self.USNPageSize = 4096
			
		cmdlineparams = u" /UsnJrnlFile:" + FULLPATH_TMPDIR + "\\" + USNJRNL
		cmdlineparams = cmdlineparams + " /OutputPath:" + FULLPATH_TMPDIR
		cmdlineparams = cmdlineparams + " /TimeZone:0.00"
		cmdlineparams = cmdlineparams + " /OutputFormat:csv"
		
		cmdlineparams = cmdlineparams + " /QuotationMark:0"
		cmdlineparams = cmdlineparams + " /Unicode:0"
		cmdlineparams = cmdlineparams + " /TSFormat:3" #DD/MM/YY HH:MM:SS.NNNNNNN
		cmdlineparams = cmdlineparams + " /TSPrecision:NanoSec"
		
		cmdlineparams = cmdlineparams + " /UsnPageSize:" + str(self.USNPageSize)
		cmdlineparams = cmdlineparams + " /ScanMode:0"
		cmdlineparams = cmdlineparams + " /TestTimestamp:1"
		
		self.cmdlineparams = cmdlineparams
		
	def ImportaCSV(self):
		#Se trata de ubicar el directorio LogFileOutputDIR
		FileOutput = FileBase().GetLastFileOutputDIR(FULLPATH_TMPDIR,'UsnJrnl_2*.csv')
			
		if len(FileOutput)>0:
			if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + FileOutput, "USNJRNL", "|", "'"): return 1
			else: return 0
	
	def Procesa(self, params):
		
		if Extractor().Extrae(params.inputfile, USNJRNL):
			
			if params.Win64: #Versión de parsers Windows de 64 bits
				self.File = self.File64
				
			self.FilePath = FileBase().GetPathMatch(params.rutaparsers,self.File)
		
			if (len(self.FilePath)>0):
				try:
					cmdlist  = self.FilePath  + " " + self.cmdlineparams
					cmdlist = cmdlist.replace("\\","/")
					FileBase().ExecuteHideStdOut(cmdlist.split(" "))
					
					try:
						if self.ImportaCSV():
							return 1
						else:
							print(u"ERROR importaCSV de USNJRNL\n")
							return 0
					except:
						print(u"ERROR importando CSV de USNJRNL\n")
						return 0
				except:
					print(u"ERROR procesando USNJRNL...\n")
					return 0
			else:
				print(u"No encontrado el parser USNJRNL...\n")
				return 0
		else:
			return 0	
		
class Mft2Csv():

	def __init__(self, cnn):
		self.cnn = cnn
		self.FilePath = u"."
		self.File = "Mft2Csv.exe"
		self.File64 = "Mft2Csv64.exe"
		self.MFTRecordSize = 1024
			
		cmdlineparams = u" /MftFile:" + FULLPATH_TMPDIR + "\\" + MFT
		cmdlineparams = cmdlineparams + " /ExtractResident:0"
		cmdlineparams = cmdlineparams + " /OutputPath:" + FULLPATH_TMPDIR
		cmdlineparams = cmdlineparams + " /TimeZone:0.00"
		cmdlineparams = cmdlineparams + " /OutputFormat:csv"
		cmdlineparams = cmdlineparams + " /BrokenMFT:1"
		cmdlineparams = cmdlineparams + " /SkipFixups:0"
		cmdlineparams = cmdlineparams + " /ScanSlack:0"
		#cmdlineparams = cmdlineparams + " /Separator:|"
		cmdlineparams = cmdlineparams + " /QuotationMark:0"
		cmdlineparams = cmdlineparams + " /Unicode:0"
		cmdlineparams = cmdlineparams + " /TSFormat:3" #DD/MM/YY HH:MM:SS.NNNNNNN
		cmdlineparams = cmdlineparams + " /TSPrecision:NanoSec"
		#cmdlineparams = cmdlineparams + " /TSPrecisionSeparator:."
		#cmdlineparams = cmdlineparams + " /SplitCsv:0"
		cmdlineparams = cmdlineparams + " /RecordSize:" + str(self.MFTRecordSize)
		
		self.cmdlineparams = cmdlineparams
		
	def ImportaCSV(self):
		#Se trata de ubicar el directorio LogFileOutputDIR
		FileOutput = FileBase().GetLastFileOutputDIR(FULLPATH_TMPDIR,'MFT_2*.csv')
		if len(FileOutput)>0:
			if Importador(self.cnn).ImportaCSV(FULLPATH_TMPDIR + "\\" + FileOutput, "MFT2CSV", "|", "'"):
				return 1
			else:
				return 0
	
	def Procesa(self, params):
	
		if Extractor().Extrae(params.inputfile, MFT):
		
			if params.Win64: #Versión de parsers Windows de 64 bits
				self.File = self.File64
				
			self.FilePath = FileBase().GetPathMatch(params.rutaparsers,self.File)
			
			if (len(self.FilePath)>0):
				try:
					stmp = self.FilePath + ' ' + self.cmdlineparams
					FileBase().ExecuteHideStdOut(stmp.split(" "))
					
					time.sleep(4)
					
					try:
						self.ImportaCSV()
						return 1
					except:
						debug(DEBUG_STATUS)
						print(u"ERROR importando CSV de MFT2CSV\n")
						return 0
				except:
					debug(DEBUG_STATUS)
					print(u"ERROR procesando MFT2CSV...\n")
					return 0
					
		else:
			return 0
		
class BDCnn(): #OK

	def __init__(self,name):
		self.name = name
		self.cnn = None
		
	def open(self):
		try:
			self.cnn = sqlite3.connect(self.name)
			return 1
		except:
			print(u"No se pudo establecer la conexión con la BD")
			return 0
					
	def close(self):
		if not (self.cnn is None):
			try: 
				self.cnn.close()
				return 1
			except:
				print(u"No se pudo cerrar la conexión con la BD")
				return 0
	
	def ExecuteSQL(self, SQL):
		try:
			SQL = SQL.replace("\\\\.\\\\","\\")
			SQL = SQL.replace("\\\\","\\")
		
			self.cnn.execute(SQL)
			self.cnn.commit()
			return 1
		except:
			debug(DEBUG_STATUS)
			return 0
			
	def Execute(self, SQL):
		try:
			self.cnn.execute(u""+SQL)
			self.cnn.commit()
			return 1
		except:
			debug(DEBUG_STATUS)
			return 0
			
	def GetCursor(self,sSQL):
		cursor = None
		try:
			cursor = self.cnn.execute(sSQL)
			self.cnn.commit()
		except:
			pass
			
		return cursor
		
	def Cursor(self):
		return self.cnn.cursor()
		
class Indicadores():

	def __init__(self,cnn):
		self.cnn = cnn
		self.PESO_MFT='1'
		self.PESO_MFT_USN='0.5'
		self.PESO_MFT_USN_LOG='0.5'
		self.PESO_MFT_LOG_IDX='0.5'

	def Procesa(self,params):
		
		SQL_Resumen = u"Select (select count(1) from (select distinct RecordOffset from resultados where FN='0' )) NumEntradas, " + \
		"(select count(1) falseadas from (Select  distinct RecordOffset  from resultados " + \
		"where  (length(MFT_SuspectedCT)>0 or length(MFT_USN_SuspectedCT)>0 or length(MFT_USN_LOG_SuspectedCT)>0 or " + \
		"length(MFT_LOG_IDX_SuspectedCT)>0 ) and FN='0'))  NumFalseadas "
		
		SQL_Coeficientes = u"Select distinct filename, Nivel, RecordOffset, DetectorStr from (Select RecordOffset, filename, " + \
		"CASE WHEN ((length(MFT_SuspectedCT)>0) and (length(MFT_USN_SuspectedCT)>0)) and ( (length(MFT_USN_LOG_SuspectedCT)>0) and (length(MFT_LOG_IDX_SuspectedCT)>0)) THEN 'ALTA' ELSE " + \
		"CASE WHEN ((length(MFT_SuspectedCT)>0) or (length(MFT_USN_SuspectedCT)>0)) or ((length(MFT_USN_LOG_SuspectedCT)>0) and (length(MFT_LOG_IDX_SuspectedCT)>0)) THEN 'MEDIA' ELSE " + \
		"CASE WHEN ( (length(MFT_USN_LOG_SuspectedCT)>0) or (length(MFT_LOG_IDX_SuspectedCT)>0)) THEN 'BAJA' ELSE '' END END END Nivel" + \
		",CASE WHEN length(MFT_SuspectedCT)>0 THEN '[*]' ELSE '[ ]' END || CASE WHEN length(MFT_USN_SuspectedCT)>0 THEN '[*]' ELSE '[ ]' END || CASE WHEN length(MFT_USN_LOG_SuspectedCT)>0 THEN '[*]' ELSE '[ ]' END || CASE WHEN length(MFT_LOG_IDX_SuspectedCT)>0 THEN '[*]' ELSE '[ ]' END DetectorStr from resultados where resultados.FN='0') calculos where length(calculos.Nivel)>0 order by calculos.Nivel "
			
		curResumen = self.cnn.GetCursor(SQL_Resumen)
		
		if not (curResumen is None):
			row = curResumen.fetchone()
			curResumen.close()
		else:
			print(u"No se pudieron generar los indicadores")
			return
			
		if row[1]>0:
			print("*** DETECTADAS  MANIPULACIONES TMS SOBRE LA IMAGEN SUMINISTRADA ***\n")
			
			print(u"Número de archivos afectados: " +  str(row[1])+ " de " + str(row[0])) 
		
			print(u"\nDetectores metodológicos:\n\n\t D1[MFT]")
			print(u"\t D2[MFT/USN]")
			print(u"\t D3[MFT/USN/LOG]")
			print(u"\t D4[MFT/LOG/IDX]")
			
			print(u"\n\nReporte de detección de manipulación TMS")
			print("Consulte el detalle en " + params.outputfile)
			print(u"========================================")
			print(u"Cred.\tDetectores\tMFTOffset  Ficheros ($SI)")
			print(u"-" * 100)
			print(u"      \t[1][2][3][4]")
			curCoef = self.cnn.GetCursor(SQL_Coeficientes)
			
			if not (curCoef is None):
				row = curCoef.fetchone()
				while not (row is None):
					print(str(row[1]) + "\t" +  str(row[3])+ "    " + str(row[2]) + " " + str(row[0]))
					row = curCoef.fetchone()
					
				curCoef.close()	
				print(u"-"*100)
			
			else:
				print("No se pudo generar los indicadores")
				return 0
				
			return 1
		else:
			print("Resultado: No se han detectado manipulaciones TMS\n")
			return 1

class Cmdline(): #OK

		
	def __init__(self):
	
		self.inputfile = u""
		self.outputfile = u""
		self.rutaparsers = u""
		self.tag = u""
		
		self.sMision = u"Utilidad para la validación de la metodología del proyecto Detección antiforense Open Source del máster Universitario UNIR en Seguridad Informática.\nEl objetivo es la inferencia de manipulaciones de timestamps (TMS) en imágenes raw sobre particiones NTFS, a partir de la información recopilada por un conjunto determinado de parsers Open Source.\n\nAutor: Jose B. Torres @2016\nLicencia GPL"
		
		self.sHelp = u"\n La sintaxis de llamada es tms-evaluador.py -i <inputfile> -o <outputfile> -p <ruta-parsers> -t <tag> \n\n\t-i: fichero imagen raw ntfs\n\t-o: fichero de resultados\n\t-p: directorio padre donde se encuentran instalados los parsers:\n\t\t SleuthKit, Log2timeline, Mft2Csv, LogFileParser, USN2Csv e IndxParse\n\n Ejemplo: tms-evaluador.py -i c:\\tms\\img.dd -o c:\\tms\\resultado.csv -p c:\\tms\\parsers -t test "
		
	def Check(self,argv):
		return self.sintaxis(argv)
		
	def sintaxis(self,argv):
		
		try:
			opts, args = getopt.getopt(argv,"hi:o:p:t",["ifile=","ofile=","path=","tag="])
		except getopt.GetoptError:
			print("tms-evaluador.py -i <inputfile> -o <outputfile> -p <ruta-parsers> -t <etiqueta>")
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print(self.sMision)
				print(self.sHelp)
				sys.exit()
			elif opt in ("-i", "--ifile"):
				self.inputfile = arg
			elif opt in ("-o", "--ofile"):
				self.outputfile = arg
			elif opt in ("-p", "--path"):
				self.rutaparsers = arg
			elif opt in ("-t", "--tag"):
				self.tag = arg
							
		if (self.inputfile=="" or self.outputfile=="" or self.rutaparsers==""):
			print(self.sHelp)
			
			return 0
		else:
			self.Win64 = FileBase().Is64Windows();
			TAG=self.tag
				
			return 1
			
	def comprobados(self):	
	
		#Comprobación del directorio temporal
		if not os.path.exists(FULLPATH_TMPDIR):
			try:
				os.makedirs(FULLPATH_TMPDIR)
			except:
				print("Error. No se puede crear el directorio temporal " + FULLPATH_TMPDIR)
				return 0
	
		if not (os.path.isfile(self.inputfile) and os.path.exists(self.rutaparsers)):
			print u"Error. No se puede acceder al fichero de imagen o a la ruta de los parsers."
			print("inputfile=" + self.inputfile)
			print("rutaparsers=" + self.rutaparsers)
	
			return 0
		else:
			#Chequea la existencia de fls
			
			global FCAT_PATH 
			FCAT_PATH = FileBase().GetPathMatch(self.rutaparsers, u"fcat.exe")
					
			return (len(FCAT_PATH)>0)
	
if __name__ == "__main__":

	params = Cmdline()
	if params.Check(sys.argv[1:]):
		if params.comprobados():
			os.system("cls")
			
			print(u"tms-evaluador v1.1\n")
			print(u"Imagen: " + params.inputfile + "\n")
						
			cnn = BDCnn(BD_FULLNAME)
			cnn.open()
						
			if Detector(cnn).Procesa(params): 
				Indicadores(cnn).Procesa(params)
			else: 
				print(u"\nFalla en la detección")
				
			print(u"BBDD generada...  " + BD_FULLNAME + "\n")
			print(u"Timeline generado...  " + params.outputfile  + ".csv\n")
			
			#elimina la carpeta temporal
			FileBase().DeleteFolder(FULLPATH_TMPDIR)
			
			cnn.close()

	