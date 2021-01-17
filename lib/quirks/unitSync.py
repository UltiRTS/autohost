import ctypes
from multiprocessing.pool import ThreadPool
import os
import fnmatch
import libarchive
from libarchive import file_reader
from termcolor import colored



class UnitSync:
	def __init__(self, startdir,libunitsync_path,username):
		self.so = ctypes.CDLL(libunitsync_path)
		self.init = self.so.Init(0, 0)
		self.write_dir = self.so.GetWritableDataDirectory()
		self.username=username
		self.startdir=startdir
		os.chdir(self.startdir)
		
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
		
		files= os.listdir(self.startdir+'/engine/maps')
		
		for file in files:
			
			if fnmatch.fnmatch(file, filename):
				
				with libarchive.file_reader(self.startdir+'/engine/maps/'+file) as reader:
					for e in reader:
					# (The entry evaluates to a filename.)
						
						if e.name[-3:]=='smf' :
							print("real map name: "+e.name)
							filename=e.name
							break;
				break;

		print(colored('[INFO]', 'green'), colored(self.username+'/unitSync: Returning actual mapfile'+filename[5:-4], 'white'))
		os.chdir(self.startdir)
		return {'mapName':filename[5:-4],'fileName':file}
	
	def mapList(self):
		mapList=''
		files= os.listdir(self.startdir+'/engine/maps')
		for file in files:
			mapList+=file+' '
		os.chdir(self.startdir)
		return mapList
		
