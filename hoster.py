import time
import _thread
import threading
#from multiprocessing import Queue
from lib.client import Client
from lib.quirks.unitSync import UnitSync
from termcolor import colored
from serverlauncher import ServerLauncher
#from lib.quirks.hosterCTL import hosterCTL
#import lib.quirks.hosterCTL
import os
import lib.cmdInterpreter
import random
from lib.server import deliver
from lib.server import AutohostServer


class Battle(threading.Thread):

	

	def __init__(self,userName, startDir, autohostFactory, password, map_file, mod_file, engineName, engineVersion, roomName, gameName,battlePort):
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
		self.autohostServer= AutohostServer
		self.battlePort    = battlePort
		self.startDir      = startDir
		self.listeners     = []
		self.client        = Client(self.battlePort,self.startDir)
		self.unitSync      = UnitSync(self.startDir, self.startDir+'/engine/libunitsync.so',self.username)
		self.isLaunched= False;
		self.server=ServerLauncher()
		self.hosterMem={}
		
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
		print("l2teams:"+str(players))    #should return something like {'Autohost_0': 0, 'GPT_2': 0, 'GPT_1': 0, 'Teresa': 0, 'GPT_3': 1}
		return(players)
	
	def gemStart(self, players,xtraOptions={}):
		if self.server.engineAlive():
			print(colored('[WARN]', 'red'), colored(self.username+': Cannot start a game twice!', 'white'))
			self.stateDump(True)
			return
		#print(self.username+" is trying to start the gem!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! example msg: "+smolString)
		#players=['Archangel',0,'Godde',1]#players, team numbers, starting from 0; an 2v1 example would be ['Archangel',0,'Xiaoming',0,'Xiaoqiang',1] 
		#ais=[] #virtually the same as the player scheme but directs bot section behavior
		xtraOptions['map']=self.map_name
		#######THE ABOVE ARGUMENTS ARE SUPPOSED TO BE RETRIEVED FROM THE CHAT#######
		numTeams=self.getAllyTeamNum(players)
		self.server.scriptGen(self.startDir,self.battlePort,players,xtraOptions,self.username,numTeams) #generate the script
		self.client.startBattle()
		self.server.launch()
		#time.sleep(2)
		self.client.stopBattle()
		
	def getAllyTeamNum(self,players):
		teamNum=1
		for player in players:
			if players[player]['team']+1>teamNum:
				teamNum=players[player]['team']+1
		return teamNum
		
	def listMap(self):
		self.mapList = random.sample(self.unitSync.mapList().split(), 5)
		self.mapList = ' '.join(self.mapList)
		print(colored('[INFO]', 'green'), colored(self.username+': Listing map with cmd:'+lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'available-maps': self.mapList+" "}), 'white'))
		
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':self.hostedby,'join':self.bid,'available-maps': self.mapList+" "}))
	
	def balance(self,ppl,gemType,leaderConfig,preDefined="false"):
		# check if started
		
		
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
			print('result:'+ str(result))
			print('ppl: '+str(ppl))
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
			self.gemStart(ppl)
			
	def stateDump(self,isLoading=False):
		if isLoading:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':'all', 'teams':self.teamConfig, 'available-maps': self.mapList, 'map':self.map_name+' '}))
		else:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'false','user':'all', 'teams':self.teamConfig, 'available-maps': self.mapList, 'map':self.map_name+' '}))
		
	def run(self):
		print(colored('[INFO]', 'green'), colored(self.username+': Loading unitsync.', 'white'))
		
		mapInfo=self.unitSync.syn2map(self.map_file)
		self.map_file=mapInfo['fileName']
		self.map_name=mapInfo['mapName']

		#print('!!!!!!!!!!!!!!!!!!!!usync chmap called')
		#self.unitSync.startHeshThread(map_file,self.mod_file)
		#unit_sync = self.unitSync.getResult()
		unit_sync = {"mapHesh":-1710297209,"modHesh":-1710297209}
		self.client.login(self.username,self.password)

		print(colored('[INFO]', 'green'), colored(self.username+': Logging in', 'white'))
		self.client.clearBuffer(self.username)
		
		_thread.start_new_thread( self.client.keepalive,(self.username,))
		self.bid=self.client.openBattle(self.username,0, 0, '*', self.battlePort, 5, unit_sync['modHesh'], 1, unit_sync['mapHesh'], self.engineName, self.engineVersion, self.map_name,  self.roomName, self.gameName)


		#hosterCTL[self.bid]="NOACTIONYET!" #init the control dictionary
		print(colored('[INFO]', 'green'), colored(self.username+': Opening Battle.', 'white'))
		#client.clearBuffer(self.username)
		self.teamConfig=''
		self.leaderConfig={}
		self.aiList=''
		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		#client.clearBuffer(self.username)
		self.client.sayChat('bus',self.listMap())
		self.client.clearBuffer(self.username)
		
		self.autohostServer = self.autohostServer('0.0.0.0',2000+self.battlePort)
		self.autohostServer.start()
		
		while True:
			ctl = deliver.get()
			#print('aaa')
			
			if ctl["bid"] != self.bid:    #do nothing if its not my business
				#deliver.task_done()
				ctl["ttl"]+=1
				print(colored('[WARN]', 'red'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' does not belong to this autohost', 'white'))
				
				if ctl["ttl"]<=20:
					deliver.put(ctl)
					time.sleep(0.1)
					continue
				else:
					print(colored('[WARN]', 'red'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' disposed of', 'white'))
					continue
				#else:
				

			else:   #do the following if the bid matches mine
				#print(ctl)
				try:
					oldVoter=' '+self.hosterMem[ctl["msg"]]
				except:
					oldVoter=''
				self.hosterMem[ctl["msg"]]=ctl['caller']+oldVoter
				numofPpl=len(self.client.getUserinChat(self.bid,self.username,''))
				print(colored('[INFO]', 'green'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' repeated '+str(len(set(self.hosterMem[ctl["msg"]].split())))+' times; minimum is '+ str(numofPpl/2), 'white'))
				if ctl['caller']==self.hostedby or len(set(self.hosterMem[ctl["msg"]].split()))> numofPpl/2:   #do the following if the bid matches mine and is from the one who hosted the btl
					
						
					
					self.hosterMem[ctl["msg"]]=''
					if ctl["action"]=="left":
						self.client.exit()
						self.autohost.free_autohost(self.username)
						# exit thread
						return
					
					if ctl["action"]=="chmap":
						try:
							self.map_file=ctl["msg"].split()[0]
							mapInfo=self.unitSync.syn2map(self.map_file)
							self.map_file=mapInfo['fileName']
							self.map_name=mapInfo['mapName']
							self.unitSync.startHeshThread(self.map_file,self.mod_file)
							unit_sync = self.unitSync.getResult()
							self.client.updateBInfo(unit_sync['mapHesh'],self.map_name)
							print(colored('[INFO]', 'green'), colored(self.username+': chmapping to '+self.map_name, 'white'))
							print(colored('[INFO]', 'green'), colored(self.username+': fileName is '+self.map_file, 'white'))
						except:
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad map cmd!', 'white'))
							

					if ctl["action"]=="start":
						ppl=self.client.getUserinChat(self.bid,self.username,self.teamConfig)
						self.balance(ppl,'custom',self.leaderConfig,self.teamConfig)
						
					
					if ctl["action"]=="teams":
						try:
							self.teamConfig=ctl["msg"]
							print('teamConfig:'+str(self.teamConfig))
							self.stateDump();
						except:
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad changeTeams cmd!', 'white'))
					
					if ctl["action"]=="leader":
						try:
							self.leaderConfig[ctl["msg"].split()[1]]=ctl["msg"].split()[2]   #for every team there will be only 1 leader; every time this runs, the leader gets overwritten
						except:
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad leader cmd!', 'white'))
