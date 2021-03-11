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
import string 
from lib.server import deliver
from lib.server import AutohostServer


class Battle(threading.Thread):

	

	def __init__(self,userName, startDir, autohostFactory, password, map_file, mod_file, engineName, engineVersion, roomName, gameName,battlePort,autohostCTLClient):
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
		self.engineToken   = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 6))
		self.battlePort    = battlePort
		self.startDir      = startDir
		self.autohostCTL=autohostCTLClient
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
	
	def gemStart(self, xtraOptions={}):
		if self.server.engineAlive():
			print(colored('[WARN]', 'red'), colored(self.username+': Cannot start a game twice!', 'white'))
			self.stateDump(True)
			return
		xtraOptions['map']=self.map_name
		#######THE ABOVE ARGUMENTS ARE SUPPOSED TO BE RETRIEVED FROM THE CHAT#######
		numTeams=self.getAllyTeamNum(self.ppl)
		self.server.scriptGen(self.startDir,self.battlePort,self.ppl,xtraOptions,self.username,numTeams) #generate the script
		self.client.startBattle()
		self.server.launch()
		#time.sleep(2)
		
	def gemStop(self):
		self.server.killServer()
		self.client.stopBattle()
		print(colored('[INFO]', 'green'), colored(self.username+': hoster exiting!', 'white'))
		
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
		
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':self.hostedby,'join':self.bid,'available-maps': self.mapList, 'hoster': self.hostedby}))
	
	def balance(self,gemType,leaderConfig,preDefined="false"):
		# check if started
		
		
		i=0
		if gemType=='fafafa':
			self.gemStart()
			
		elif gemType=="teams":
			for player in self.ppl:
				
				if i>=len(self.ppl)/2:
					#print('aaa')
					self.ppl[player]['team']=1
					#ppl.values()[i]['team']=0
				else:
					#print('bbb')
					self.ppl[player]['team']=0
					#player['team']=1
					#ppl.values()[i]['team']=1
				i+=1
			print('player config'+str(self.ppl))
			self.gemStart(2)
			
		elif gemType=="pve":
			self.gemStart()
		
		elif gemType=="custom":
			result=self.letter2Teams(preDefined)
			print('result:'+ str(result))
			print('ppl: '+str(self.ppl))
			for player in self.ppl:                      #apply team designation to ppl matrix
				try:
					self.ppl[player]['team']=result[player]
				except:
					print(colored('[INFO]', 'green'), colored(self.username+': Player '+player+" has unassigned team!", 'white'))
					
			## TODO: test
			if leaderConfig == '':
				leader = list(self.ppl.keys())[0]
				self.ppl[leader]['isLeader'] = True
			else:
				self.ppl[leaderConfig]['isLeader'] = True
				
						
			print('player custom config'+str(self.ppl))
			self.gemStart()
			
	def stateDump(self,isLoading=False):
		
		if isLoading:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':'all', 'teams':self.teamConfig,'engineToken':self.engineToken, 'available-maps': self.mapList, 'totalPpl':str(len(self.client.getUserinChat(self.bid,self.username,''))),'leader': self.leaderConfig,'map':self.map_name, 'hoster': str(self.hostedby) + ' '}))
		else:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'false','user':'all', 'teams':self.teamConfig, 'engineToken':self.engineToken,'available-maps': self.mapList, 'totalPpl':str(len(self.client.getUserinChat(self.bid,self.username,''))),'leader': self.leaderConfig, 'map':self.map_name, 'hoster': str(self.hostedby) + ' '}))
	
	def joinasSpec(self,usrName):
		self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':usrName,'engineToken':self.engineToken,'joinasSpec':'true '}))
	
	def rejoin(self, usrName):
		self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':usrName,'engineToken':self.engineToken,'joinasSpec':'true '}))
	
	
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
		self.autohostCTL.joinChat(self.bid)

		#hosterCTL[self.bid]="NOACTIONYET!" #init the control dictionary
		print(colored('[INFO]', 'green'), colored(self.username+': Opening Battle.', 'white'))
		#client.clearBuffer(self.username)
		self.teamConfig=''
		#OLD: self.leaderConfig={}
		self.leaderConfig=""
		self.aiList=''
		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		#client.clearBuffer(self.username)
		self.client.sayChat('bus', self.listMap()+" ")
		self.client.clearBuffer(self.username)
		
		self.autohostServer= AutohostServer('0.0.0.0',2000+self.battlePort,self.hostedby,self.bid)
		self.autohostServer.start()
		
		while True:
			ctl = deliver.get()
			#print('aaa')
			
			if ctl["bid"] != self.bid:    #do nothing if its not my business
				#deliver.task_done()
				ctl["ttl"]+=1
				print(colored('[WARN]', 'red'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' does not belong to this autohost', 'white'))
				
				if ctl["ttl"]<=200:
					deliver.put(ctl)
					time.sleep(0.01)
					continue
				else:
					print(colored('[WARN]', 'red'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' disposed of', 'white'))
					continue
				#else:
				

			else:   #do the following if the bid matches mine
				#print(ctl)
				
				if ctl['action'] == 'joinasSpec':     ##everyone commands, commands that everyone can run
					if ctl['caller'] in [self.ppl.strip() for self.ppl in self.teamConfig.split(' ') ]:
						self.rejoin(ctl['caller'])
					else:
						self.autohostServer.autohostInterfaceSayChat('/AddUser '+ctl['caller'] + ' '+self.engineToken + ' 1')
						time.sleep(1)
						self.joinasSpec(ctl['caller'])
						#print(colored('[INFO]', 'white'), 'Connection allowed')
						
						
				if ctl['action'] == 'forward2AutohostInterface':     ##everyone commands, commands that everyone can run
						self.autohostServer.autohostInterfaceSayChat('/ChatAll '+ctl['caller'] + '$ '+ctl['msg'])
						
				if ctl['action'] == 'sayBtlRoom': 		
					self.autohostCTL.sayChat(str(self.bid),ctl['msg'])
					
				if ctl['caller']==self.hostedby: #(non pollable&host only commands)
					
					if ctl["action"]=="left":
						self.client.exit()
						self.autohost.free_autohost(self.username)
						# exit thread
						return
				
				
				try:
					oldVoter=' '+self.hosterMem[ctl["msg"]]
				except:
					oldVoter=''
				self.hosterMem[ctl["msg"]]=ctl['caller']+oldVoter
				numofPpl=len(self.client.getUserinChat(self.bid,self.username,''))
				print(colored('[INFO]', 'green'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' repeated '+str(len(set(self.hosterMem[ctl["msg"]].split())))+' times; minimum is '+ str(numofPpl/2), 'white'))

				if ctl['caller']==self.hostedby or len(set(self.hosterMem[ctl["msg"]].split()))> numofPpl/2:   #do the following if the bid matches mine and is from the one who hosted the btl(pollable &host only commands)
					self.hosterMem[ctl["msg"]]=''
					
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
						self.ppl=self.client.getUserinChat(self.bid,self.username,self.teamConfig)
						self.balance('custom',self.leaderConfig,self.teamConfig)
						
					if ctl["action"]=="exit":
						self.gemStop()
						
					
					if ctl["action"]=="teams":
						try:
							self.teamConfig=ctl["msg"]
							#print('teamConfig:'+str(self.teamConfig))
							self.stateDump()
						except Exception as e:
							print(e)
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad changeTeams cmd!', 'white'))
					
					if ctl["action"]=="leader":
						try:
							# OLD: self.leaderConfig[ctl["msg"].split()[1]]=ctl["msg"].split()[2]   #for every team there will be only 1 leader; every time this runs, the leader gets overwritten
							self.leaderConfig = ctl["msg"].split()[1]
							self.stateDump()
						except:
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad leader cmd!', 'white'))

					if ctl['action'] =='cheat':
						self.autohostServer.autohostInterfaceSayChat('/Cheat')
						self.autohostServer.autohostInterfaceSayChat('/NoCost')
						
						print(colored('[INFO]', 'green'), colored(self.username+': Enabling cheat for this hoster!'))
