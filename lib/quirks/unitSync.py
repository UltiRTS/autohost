import ctypes
from multiprocessing.pool import ThreadPool
import os
import fnmatch
import libarchive
from libarchive import file_reader



class UnitSync:
	def __init__(self, libunitsync_path):
		self.so = ctypes.CDLL(libunitsync_path)
		self.init = self.so.Init(0, 0)
		self.write_dir = self.so.GetWritableDataDirectory()

	def startHeshThread(self, map_path, mod_hesh):
		self.pool = ThreadPool(processes=1)
		self.async_result = self.pool.apply_async(
		self.getHesh, (map_path, mod_hesh))

	def getResult(self,startDir):
		os.chdir(startDir)
		return self.async_result.get()

	def getHesh(self, map_path, mod_hesh):
		unit_sync = {
			'mapHesh': self.so.GetMapChecksumFromName(map_path.encode()),
			'modHesh': self.so.GetPrimaryModChecksumFromName(mod_hesh.encode()),
		}
		return unit_sync
	
	def syn2map(self,filename):
		files= os.listdir('./engine/maps')
		for file in files:
			if fnmatch.fnmatch(file, filename):
				print("Actual Mapname="+file);
				with libarchive.file_reader(self.startDir+'./engine/maps/'+file) as reader:
					for e in reader:
					# (The entry evaluates to a filename.)
						print(e)
						if e.name[-3:]=='smf' :
							print("real map name: "+e.name)
							filename=e.name
							break;
				break;
		print("returning name"+ filename[5:-4])
		return filename[5:-4]
	
	def mapList(self):
		mapList=''
		files= os.listdir('./engine/maps')
		for file in files:
			mapList+=file+' '
		return mapList
		
