import time
import _thread
import threading
from multiprocessing import Queue
from lib.client import Client
from lib.quirks.unitSync import UnitSync
from termcolor import colored
from serverlauncher import ServerLauncher
from lib.quirks.hosterCTL import hosterCTL
import lib.quirks.hosterCTL
import os
import lib.cmdInterpreter
import random

q = Queue()
l = threading.Lock()

class Battle(threading.Thread):

	

	def __init__(self,userName, startDir,q, autohostFactory, password, map_file, mod_file, engineName, engineVersion, roomName, gameName,battlePort):
		threading.Thread.__init__(self)
		self.autohost = autohostFactory;
		self.username = autohostFactory.new_autohost()
		self.hostedby = userName
		print(colored('[INFO]', 'green'), colored(self.username+': Autohost account received!', 'white'))
		self.password      = password
		self.map_file      = map_file
		self.mod_file      = mod_file
		self.engineName    = engineName
		self.engineVersion = engineVersion
		self.roomName      = roomName
		self.gameName      = gameName
		self.q             = q
		self.battlePort    = battlePort
		self.startDir      = startDir
		self.listeners     = []
		self.client        = Client(self.battlePort,self.startDir)
		self.unitSync      = UnitSync(self.startDir, self.startDir+'/engine/libunitsync.so',self.username)
	
	def letter2Teams(self,playerCMD):
		receivedStr= playerCMD.split(" ")
		n=0
		cmdDict={}
		players={}
		while n<len(receivedStr)-1:
			cmdDict[receivedStr[n+1]]=[]
			n=n+2
		n=0

		while n<len(receivedStr)-1:
			cmdDict[receivedStr[n+1]].insert(0,receivedStr[n])
			n=n+2
		i=0

		for key in cmdDict:
			for player in cmdDict[key]:
				players[player]=i
			i=i+1
		print("l2teams:"+str(players))
		return(players)
	
	def gemStart(self, players,numTeams,xtraOptions={}):
		#print(self.username+" is trying to start the gem!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! example msg: "+smolString)
		#players=['Archangel',0,'Godde',1]#players, team numbers, starting from 0; an 2v1 example would be ['Archangel',0,'Xiaoming',0,'Xiaoqiang',1] 
		#ais=[] #virtually the same as the player scheme but directs bot section behavior
		xtraOptions['map']=self.map_file 
		#######THE ABOVE ARGUMENTS ARE SUPPOSED TO BE RETRIEVED FROM THE CHAT#######
		server=ServerLauncher(self.startDir,self.battlePort,players,xtraOptions,self.username,numTeams)
		server.scriptGen() #generate the script
		self.client.startBattle()
		server.launch()
		#time.sleep(2)
		self.client.stopBattle()
		
	def listMap(self):
		mapList = random.sample(self.unitSync.mapList().split(), 5)
		mapList = ' '.join(mapList)
		print(colored('[INFO]', 'green'), colored(self.username+': Listing map with cmd:'+lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'available-maps': mapList}), 'white'))
		
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':self.hostedby,'room':self.bid,'available-maps': mapList}))
	
	def balance(self,ppl,gemType,leaderConfig,preDefined="false"):
		i=0
		if gemType=='fafafa':
			self.gemStart()
			
		elif gemType=="teams":
			for player in ppl:
				
				if i>=len(ppl)/2:
					#print('aaa')
					ppl[player]['team']=1
					#ppl.values()[i]['team']=0
				else:
					#print('bbb')
					ppl[player]['team']=0
					#player['team']=1
					#ppl.values()[i]['team']=1
				i+=1
			print('player config'+str(ppl))
			self.gemStart(ppl,2)
			
		elif gemType=="pve":
			self.gemStart()
		
		elif gemType=="custom":
			result=self.letter2Teams(preDefined)
			for player in ppl:                      #apply team designation to ppl matrix
				try:
					ppl[player]['team']=result[player]
				except:
					print(colored('[INFO]', 'green'), colored(self.username+': Player '+player+" has unassigned team!", 'white'))
					
			for team in leaderConfig:             #for every leader, find the player in the ppl matrix, and set their leader status to true
				for player in ppl:
					#print('currently in team '+str(team))
					#print('currently setting up'+player+' in team '+str(ppl[player]['team']))
					if leaderConfig[team]==player:
						ppl[player]['isLeader']=True
						
			print('player custom config'+str(ppl))
			self.gemStart(ppl,2)
			
	def teamAssign(self,teamConfig):
		print(colored('[INFO]', 'green'), colored(self.username+': Returning teamConfig:'+lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'player': teamConfig}), 'white'))
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':'all','room':self.bid,'player': teamConfig}))
	
	def run(self):
		print(colored('[INFO]', 'green'), colored(self.username+': Loading unitsync.', 'white'))
		
		mapInfo=self.unitSync.syn2map(self.map_file)
		map_file=mapInfo['fileName']
		map_name=mapInfo['mapName']

		#print('!!!!!!!!!!!!!!!!!!!!usync chmap called')
		#self.unitSync.startHeshThread(map_file,self.mod_file)
		#unit_sync = self.unitSync.getResult()
		unit_sync = {"mapHesh":-1710297209,"modHesh":-1710297209}
		self.client.login(self.username,self.password)

		print(colored('[INFO]', 'green'), colored(self.username+': Logging in', 'white'))
		self.client.clearBuffer(self.username)
		
		_thread.start_new_thread( self.client.keepalive,(self.username,))
		self.bid=self.client.openBattle(self.username,0, 0, '*', self.battlePort, 5, unit_sync['modHesh'], 1, unit_sync['mapHesh'], self.engineName, self.engineVersion, map_name,  self.roomName, self.gameName)


	#	hosterCTL[self.bid]="NOACTIONYET!" #init the control dictionary
		ctl = {
			"bid": self.bid,
			"msg": "NOACTIONYET!"
		}
		q.put(ctl)

		print(colored('[INFO]', 'green'), colored(self.username+': Opening Battle.', 'white'))
		#client.clearBuffer(self.username)
		teamConfig=''
		leaderConfig={}
		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		#client.clearBuffer(self.username)
		self.client.sayChat('bus',self.listMap())
		self.client.clearBuffer(self.username)

		l.acquire()
		while True:
			#client.ping(self.username)
			time.sleep(1)
			#print(self.hostedby+"is running with bid"+self.bid)
#			if hosterCTL[self.bid].startswith("left") and self.hostedby in hosterCTL[self.bid]:
#				self.client.exit()
#				self.autohost.free_autohost(self.username)
#				return
#			
#			if hosterCTL[self.bid].startswith("chmap") and self.hostedby in hosterCTL[self.bid]:
#				self.map_file=hosterCTL[self.bid].split()[1]
#				mapInfo=self.unitSync.syn2map(self.map_file)
#				map_file=mapInfo['fileName']
#				map_name=mapInfo['mapName']
#				#print('!!!!!!!!!!!!!!!!!!!!usync chmap called')
#				try:
#					self.unitSync.startHeshThread(map_file,self.mod_file)
#					unit_sync = self.unitSync.getResult()
#					self.client.updateBInfo(unit_sync['mapHesh'],map_name)
#				except:
#					print(colored('[INFO]', 'red'), colored(self.username+': dropping bad map cmd!', 'white'))
#				hosterCTL[self.bid]='null'
#			
#			if hosterCTL[self.bid].startswith("start") and self.hostedby in hosterCTL[self.bid]:
#				ppl=self.client.getUserinChat(self.bid,self.username)
#				#self.client.getUserinChat(self.bid,self.username)
#				
#				self.balance(ppl,'custom',leaderConfig,teamConfig)
#				hosterCTL[self.bid]='null'
#
#			if hosterCTL[self.bid].startswith("changeTeams") and self.hostedby in hosterCTL[self.bid]:
#				teamConfig=' '
#				teamConfig=teamConfig.join(hosterCTL[self.bid].split()[2:])
#				print('teamConfig:'+str(teamConfig))
#				hosterCTL[self.bid]='null'
#				self.client.sayChat('bus',self.teamAssign(teamConfig))
#				
#			if hosterCTL[self.bid].startswith("leader") and hosterCTL[self.bid].endswith(self.hostedby):
#				
#				leaderConfig[hosterCTL[self.bid].split()[1]]=hosterCTL[self.bid].split()[2]   #for every team there will be only 1 leader; every time this runs, the leader gets overwritten
#				print(hosterCTL[self.bid].split()[1:3])
#				hosterCTL[self.bid]='null'
				
			if not q.empty():
				ctl = q.get()
			else:
				continue

			if ctl["bid"] != self.bid:
				q.put(ctl)
				continue
			else:
				if ctl["msg"].startwith("left") and self.hostedby in ctl["msg"]:
					self.client.exit()
					self.autohost.free_autohost(self.username)
					return

				if ctl["msg"].startwith("chmap") and self.hostedby in ctl["msg"]:
					self.map_file=ctl["msg"].split()[1]
					mapInfo=self.unitSync.syn2map(self.map_file)
					map_file=mapInfo['fileName']
					map_name=mapInfo['mapName']
					#print('!!!!!!!!!!!!!!!!!!!!usync chmap called')
					try:
						self.unitSync.startHeshThread(map_file,self.mod_file)
						unit_sync = self.unitSync.getResult()
						self.client.updateBInfo(unit_sync['mapHesh'],map_name)
					except:
						print(colored('[INFO]', 'red'), colored(self.username+': dropping bad map cmd!', 'white'))
					ctl["msg"] = "null"
					q.put(ctl)
				
				if ctl["msg"].startwith("start") and self.hostedby in ctl["msg"]:
					ppl=self.client.getUserinChat(self.bid,self.username)
					#self.client.getUserinChat(self.bid,self.username)
					
					self.balance(ppl,'custom',leaderConfig,teamConfig)
					ctl["msg"] = "null"
					q.put(ctl)
			
				if ctl["msg"].startwith("changeTeams") and self.hostedby in ctl["msg"]:
					teamConfig=' '
					teamConfig=teamConfig.join(ctl["msg"].split()[2:])
					print('teamConfig:'+str(teamConfig))
					ctl["msg"] = "null"
					q.put(ctl)
					self.client.sayChat('bus',self.teamAssign(teamConfig))
				
				if ctl["msg"].startwith("leader") and self.hostedby in ctl["msg"]:
					leaderConfig[ctl["msg"].split()[1]]=ctl["msg"].split()[2]   #for every team there will be only 1 leader; every time this runs, the leader gets overwritten
					print(ctl["msg"].split()[1:3])
					ctl["msg"] = "null"
					q.put(ctl)

				
				if lib.quirks.hosterCTL.isInetDebug:
					self.client.clearBuffer(self.username)
            
			if not l.locked():
				l.acquire()
#sock.close()
