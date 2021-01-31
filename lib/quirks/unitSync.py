import ctypes
from multiprocessing.pool import ThreadPool
import os
import fnmatch
import re
from termcolor import colored


class UnitSync:
	def __init__(self, startdir,libunitsync_path,username):
		self.so = ctypes.CDLL(libunitsync_path)
		self.init = self.so.Init(0, 0)
		self.write_dir = self.so.GetWritableDataDirectory()
		self.username=username
		self.startdir=startdir
		os.chdir(self.startdir)
		# Some Dynamic functions
		self._getMapCount = self.so.GetMapCount
		self._getMapName = self.so.GetMapName
		self._getMapFileName = self.so.GetMapFileName
		# output settings
		self._getMapCount.restype = ctypes.c_int
		self._getMapName.restype = ctypes.c_char_p
		self._getMapFileName.restype = ctypes.c_char_p
		
	def startHeshThread(self, map_path, mod_hesh):
		self.pool = ThreadPool(processes=1)
		self.async_result = self.pool.apply_async(
		self.getHesh, (map_path, mod_hesh))
		os.chdir(self.startdir)

	def getResult(self):
		os.chdir(self.startdir)
		
		return self.async_result.get()

	def getHesh(self, map_path, mod_hesh):
		unit_sync = {
			'mapHesh': self.so.GetMapChecksumFromName(map_path.encode()),
			'modHesh': self.so.GetPrimaryModChecksumFromName(mod_hesh.encode()),
		}
		os.chdir(self.startdir)
		return unit_sync
	
	def syn2map(self,filename):
		patt = re.compile( fnmatch.translate(filename), re.I )

		mapCount = self._getMapCount()
		for i in range(mapCount):
			mapName = self._getMapName(i).decode('utf-8')
			print('comparing'+str(patt)+' against '+str(mapName))
			if patt.match(mapName):
				fname = self._getMapFileName(i).decode('utf-8')
				break
		else:
			fname = mapName = None
			print(colored('[ERRO]', 'red'), colored('map not found', 'white'))
			return {'mapName': None, 'fileName': None}

		mapName, fname = fname, mapName
		mapName = mapName[5:-4]
		fname = fname.lower().replace(' ', '_') + ".sd7"

		print( colored('[INFO]', 'green'), colored(self.username+'/unitSync: Returning actual mapfile: '+fname, 'white'))
		return {'mapName': mapName, 'fileName': fname}
	
	def mapList(self):
		mapList=''
		mapCount = self._getMapCount()
		for i in range(mapCount):
			mapList+=self._getMapName(i).decode('utf-8')+' '
		os.chdir(self.startdir)
		return mapList
