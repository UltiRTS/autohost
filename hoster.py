import time
import _thread
import threading
from multiprocessing import Queue
from lib.client import Client
from lib.quirks.unitSync import UnitSync
from termcolor import colored
from serverlauncher import ServerLauncher
from lib.quirks.hosterCTL import hosterCTL

class Battle(threading.Thread):

	

	def __init__(self,userName, startDir,q, autohostFactory, password, map_file, mod_file, engineName, engineVersion, mapName, roomName, gameName,battlePort):
		threading.Thread.__init__(self)
		self.autohost= autohostFactory;
		self.username = autohostFactory.new_autohost()
		self.hostedby=userName
		print(colored('[INFO]', 'green'), colored(self.username+': Autohost account received!', 'white'))
		self.password=password
		self.map_file=map_file
		self.mod_file=mod_file
		self.engineName=engineName
		self.engineVersion=engineVersion
		self.mapName=mapName
		self.roomName=roomName
		self.gameName=gameName
		self.q=q
		self.battlePort=battlePort
		self.startDir=startDir
		self.listeners = []
		self.client = Client(self.battlePort,self.startDir)

	def run(self):
		

		print(colored('[INFO]', 'green'), colored(self.username+': Loading unitsync.', 'white'))
		unitSync = UnitSync( self.startDir+'/engine/libunitsync.so')
		unitSync.startHeshThread(self.map_file,self.mod_file)
		unit_sync = unitSync.getResult(self.startDir)


		
		
		
		self.client.login(self.username,self.password)

		print(colored('[INFO]', 'green'), colored(self.username+': Logging in', 'white'))
		self.client.clearBuffer(self.username)
		
		_thread.start_new_thread( self.client.keepalive,(self.username,))
		self.bid=self.client.openBattle(0, 0, '*', self.battlePort, 5, unit_sync['modHesh'], 1, unit_sync['mapHesh'], self.engineName, self.engineVersion, self.mapName,  self.roomName, self.gameName)


		hosterCTL[self.bid]="NOACTIONYET!" #init the control dictionary
		print(colored('[INFO]', 'green'), colored(self.username+': Opening Battle.', 'white'))
		#client.clearBuffer(self.username)

		
		
		#client.clearBuffer(self.username)
		
		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		#client.clearBuffer(self.username)
		
		self.client.clearBuffer(self.username)
		while True:
			#client.ping(self.username)
			time.sleep(1)
			#print(self.hostedby+"is running with bid"+self.bid)
			if hosterCTL[self.bid].startswith("left") and self.hostedby in hosterCTL[self.bid]:
				self.client.exit()
				self.autohost.free_autohost(self.username)
				return
			

		

			
	def gemStart(self, smolString):
		#print(self.username+" is trying to start the gem!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! example msg: "+smolString)
		players=['Archangel',0]#players, team numbers, starting from 0; an 2v1 example would be ['Archangel',0,'Xiaoming',0,'Xiaoqiang',1] 
		ais=['CircuitAI',1] #virtually the same as the player scheme but direct bot section behavior
		args=['map','co*ca*re*.sd7'] #command arguments.
		#######THE ABOVE ARGUMENTS ARE SUPPOSED TO BE RETRIEVED FROM THE CHAT#######
		server=ServerLauncher(self.startDir,self.battlePort,players,ais,args,self.username,self.autohost)
		server.scriptGen() #generate the script
		self.client.startBattle()
		server.launch()
		#time.sleep(2)
#sock.close()
