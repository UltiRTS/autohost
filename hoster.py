import time
import _thread
import threading
from lib.client import Client
from lib.quirks.unitSync import UnitSync
from termcolor import colored
from serverlauncher import ServerLauncher
import lib.cmdInterpreter
import random
import string 
import datetime
from lib.server import deliver
from lib.server import AutohostServer
from lib.dbpastgameRecorder import recordThisReplay

class Battle(threading.Thread):
	bid=0
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
		
	def getPplMaxIndex(self):
		theMax = 0
		for uName, uInfo in self.ppl.items():
			if uInfo['index'] > theMax:
				theMax = uInfo['index']

		return theMax
			
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
		
		return(players)
	
	def gemStart(self, xtraOptions={}):
		if self.server.engineAlive():
			print(colored('[WARN]', 'red'), colored(self.username+': Cannot start a game twice!', 'white'))
			self.stateDump(True)
			return
		xtraOptions['map']=self.map_name
		
		numTeams=self.getAllyTeamNum(self.ppl)
		self.server.scriptGen(self.startDir,self.battlePort,self.ppl,xtraOptions,self.username,numTeams) #generate the script
		self.client.startBattle()
		self.server.launch()
		
		
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
			#print('result:'+ str(result))
			#print('ppl: '+str(self.ppl))
			for player in self.ppl:                      #apply team designation to ppl matrix
				try:
					self.ppl[player]['team']=result[player]
				except:
					print(colored('[INFO]', 'green'), colored(self.username+': Player '+player+" has unassigned team!", 'white'))
					
			## TODO: test
			try:
				self.ppl[self.leaderConfig]['isLeader'] = True
			except:
				leader = list(self.ppl.keys())[0]
				self.ppl[leader]['isLeader'] = True
				print(colored('[WARN]', 'red'), colored(self.username+': leader config'+self.leaderConfig+" is not valid.", 'white'))
				
						
			print('player custom config'+str(self.ppl))
			print(colored('[INFO]', 'green'), colored(self.username+': player custom config'+str(self.ppl), 'white'))
			self.gemStart()
			
	def parseIngameMsg(self, msg):
		toHandle = msg.split(r'\r')[1]
		userIdStr = toHandle[2:4]
		userId = int(userIdStr, 16)
		message = toHandle[8:-1]
		chatUser = None
		print(self.ppl)
		for user, uInfo in self.ppl.items():
			if uInfo['index'] == userId:
				chatUser = user
				break
		
		if userId in self.spectors.keys():
			chatUser = self.spectors[userId]

		print("userid: ", userId, " User: ", chatUser)

		return user, message

	def stateDump(self,isLoading=False):
		
		if isLoading:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':'all', 'teams':self.teamConfig,'engineToken':self.engineToken, 'available-maps': self.mapList, 'totalPpl':str(len(self.client.getUserinChat(self.bid,self.username,''))),'leader': self.leaderConfig,'map':self.map_name, 'hoster': str(self.hostedby), 'comment': self.comment, 'ingameChat': self.ingameChatMsg + ' '}))
		else:
			self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'false','user':'all', 'teams':self.teamConfig, 'engineToken':self.engineToken,'available-maps': self.mapList, 'totalPpl':str(len(self.client.getUserinChat(self.bid,self.username,''))),'leader': self.leaderConfig, 'map':self.map_name, 'hoster': str(self.hostedby), 'comment': self.comment, 'ingameChat': self.ingameChatMsg + ' '}))
	
	def joinasSpec(self,usrName):
		self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':usrName,'engineToken':self.engineToken,'joinasSpec':'true '}))
	
	def rejoin(self, usrName):
		self.client.sayChat('bus',lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'loading':'true','user':usrName,'engineToken':self.engineToken,'joinasSpec':'true '}))
	
	
	def run(self):
		print(colored('[INFO]', 'green'), colored(self.username+': Loading unitsync.', 'white'))
		
		mapInfo=self.unitSync.syn2map(self.map_file)
		self.map_file=mapInfo['fileName']
		self.map_name=mapInfo['mapName']

		unit_sync = {"mapHesh":-1710297209,"modHesh":-1710297209}
		self.client.login(self.username,self.password)

		print(colored('[INFO]', 'green'), colored(self.username+': Logging in', 'white'))
		self.client.clearBuffer(self.username)
		
		_thread.start_new_thread( self.client.keepalive,(self.username,))
		bid=self.bid=self.client.openBattle(self.username,0, 0, '*', self.battlePort, 5, unit_sync['modHesh'], 1, unit_sync['mapHesh'], self.engineName, self.engineVersion, self.map_name,  self.roomName, self.gameName)
		self.autohostCTL.joinChat(self.bid)
		print(colored('[INFO]', 'green'), colored(self.username+': Opening Battle.', 'white'))
		self.teamConfig=''
		self.leaderConfig=""
		
		self.comment = ''	
		self.ingameChatMsg = ''
		self.ppl = {}
		self.spectors = {}

		self.preSpectors = []

		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		self.client.sayChat('bus', self.listMap()+" ")
		self.client.clearBuffer(self.username)
		
		self.autohostServer= AutohostServer('0.0.0.0',2000+self.battlePort,self.hostedby,self.bid)
		self.autohostServer.start()
		
		while True:
			ctl = deliver.get()
			#print('aaa')
			
			if ctl["bid"] != self.bid:    #do nothing if its not my business
				#deliver.task_done()
				print(colored('[WARN]', 'red'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg']+' marked as '+ctl["bid"]+' does not belong to this autohost, halting'+self.bid, 'white'))
				deliver.put(ctl)
				deliver.join()
				
				#else:
				

			else:   #do the following if the bid matches mine
				#print(ctl)
				deliver.task_done()
				if ctl['action'] == 'specOrder':
					if self.server.engineAlive():
						print(colored('[ERRO]', 'red'), ": engine started, spec order failed.")
					toBeSpec = ctl['msg'].split(' ')
					if ctl['caller'] == self.hostedby:
						for spector in toBeSpec:
							if spector not in self.preSpectors:
								self.preSpectors.append(spector)
					elif ctl['caller'] in toBeSpec:
						if ctl['caller'] not in self.preSpectors:
							self.preSpectors.append(ctl['caller'])

					print(self.preSpectors)

					continue


				if ctl['action'] == 'joinasSpec':     ##everyone commands, commands that everyone can run
					if ctl['caller'] in [ppl.strip() for ppl in self.teamConfig.split(' ') ]:
						self.rejoin(ctl['caller'])
					else:
						self.autohostServer.autohostInterfaceSayChat('/AddUser '+ctl['caller'] + ' '+self.engineToken + ' 1')
						if ctl['caller'] not in self.spectors.values():
							self.pplIngameCount += 1	
							self.spectors[self.pplIngameCount] = ctl['caller']
					
						time.sleep(1)
						self.joinasSpec(ctl['caller'])
					continue
					
						
						
				if ctl['action'] == 'forward2AutohostInterface':     ##everyone commands, commands that everyone can run
					if self.server.engineAlive():
						self.autohostServer.autohostInterfaceSayChat('/ChatAll')
						self.autohostServer.autohostInterfaceSayChat(ctl['caller'] + '$ ' + ctl['msg'])
					continue
						
				if ctl['action'] == 'sayBtlRoom': 		
					print("GOT: ", ctl['msg'])
					user, message = self.parseIngameMsg(ctl['msg'])
					self.ingameChatMsg = user + ' ' + message
					self.stateDump()
					#self.autohostCTL.sayChat(str(self.bid),user + " said: " + message)
					continue
					
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
					
					if ctl['action'] == 'comment':
						self.comment = ctl['msg']
						self.stateDump()

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

						for player in self.ppl:
							if player in self.preSpectors:
								self.ppl[player]['isSpector'] = True

						print(self.ppl)
						self.pplIngameCount = self.getPplMaxIndex()
						print(colored('[INFO]', 'cyan'), "ppl: ", self.ppl)
						self.balance('custom',self.leaderConfig,self.teamConfig)
						
					if ctl["action"]=="exit":
						recordThisReplay(self.bid,str(datetime.datetime.utcnow()), self.map_name, self.hostedby,'unknown', str(self.ppl),'unknown', 'unknown',0,'01:30:02')
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
							if not ctl["msg"].split()[1]=='':
								self.leaderConfig = ctl["msg"].split()[1]
								print(colored('[INFO]', 'cyan'), "LeaderInfo: ", self.leaderConfig)
								self.stateDump()
						except:
							print(colored('[WARN]', 'red'), colored(self.username+': dropping bad leader cmd!', 'white'))

					if ctl['action'] =='cheat':
						self.autohostServer.autohostInterfaceSayChat('/Cheat')
						#self.autohostServer.autohostInterfaceSayChat('/NoCost')
						
						print(colored('[INFO]', 'green'), colored(self.username+': Enabling cheat for this hoster!'))
