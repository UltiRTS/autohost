import time
import _thread
import threading
#from multiprocessing import Queue
import queue
from lib.client import Client
from lib.quirks.unitSync import UnitSync
from termcolor import colored
from serverlauncher import ServerLauncher
#from lib.quirks.hosterCTL import hosterCTL
#import lib.quirks.hosterCTL
import os
import lib.cmdInterpreter
import random


deliver = queue.Queue()

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
		xtraOptions['map']=self.map_name
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
		
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':self.hostedby,'action':'listMap','room':self.bid,'available-maps': mapList}))
	
	def balance(self,ppl,gemType,leaderConfig,preDefined="false"):
		# check if started
		if ServerLauncher.engineAlive():
			return
		
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
			self.gemStart(ppl,2)
			
	def teamAssign(self,teamConfig):
		print(colored('[INFO]', 'green'), colored(self.username+': Returning teamConfig:'+lib.cmdInterpreter.cmdWrite('lobbyctl', {'room':self.bid,'player': teamConfig}), 'white'))
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':'all','action':'teamAssign','room':self.bid,'player': teamConfig}))
	
	def aiResponse(self,AI):
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':'all','action':'aiAdd','room':self.bid,'AI': AI}))
	
	def kaiResponse(self,AI):
		return (lib.cmdInterpreter.cmdWrite('lobbyctl', {'user':'all','action':'aiKill','room':self.bid,'AI': AI}))
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
		teamConfig=''
		leaderConfig={}
		aiList=''
		self.client.joinChat('bus')
		print(colored('[INFO]', 'green'), colored(self.username+': Joining Battle Chat.', 'white'))
		#client.clearBuffer(self.username)
		self.client.sayChat('bus',self.listMap())
		self.client.clearBuffer(self.username)

		while True:
			#client.ping(self.username)
			#time.sleep(1)
			#print(self.hostedby+"is running with bid"+self.bid)

			ctl = deliver.get()
			print(ctl)
			print(colored('[INFO]', 'green'), colored(self.username+' New Msg from'+ctl['caller']+': '+ctl['msg'], 'white'))
			if ctl["bid"] != self.bid:    #do nothing if its not my business
				#deliver.task_done()
				ctl["ttl"]+=1
				if ctl["ttl"]>=20:
					continue
				#else:
					deliver.put(ctl)
				#deliver.join()
			else:   #do the following if the bid matches mine
				msg = ctl["msg"]	
				if ctl['caller']==self.hostedby:   #do the following if the bid matches mine and is from the one who hosted the btl
					if msg.startswith("left"):
						self.client.exit()
						self.autohost.free_autohost(self.username)
						# exit thread
						return
					if msg.startswith("chmap"):
						self.map_file=msg.split()[1]
						mapInfo=self.unitSync.syn2map(self.map_file)
						self.map_file=mapInfo['fileName']
						self.map_name=mapInfo['mapName']
							#print('!!!!!!!!!!!!!!!!!!!!usync chmap called')
						try:
							self.unitSync.startHeshThread(self.map_file,self.mod_file)
							unit_sync = self.unitSync.getResult()
							self.client.updateBInfo(unit_sync['mapHesh'],self.map_name)
							print(colored('[INFO]', 'green'), colored(self.username+': chmapping to '+self.map_name, 'white'))
							print(colored('[INFO]', 'green'), colored(self.username+': fileName is '+self.map_file, 'white'))

						except:
							print(colored('[INFO]', 'red'), colored(self.username+': dropping bad map cmd!', 'white'))
							#hosterCTL[self.bid]='null'

					if msg.startswith("start"):
						ppl=self.client.getUserinChat(self.bid,self.username,aiList)
							#self.client.getUserinChat(self.bid,self.username)
							
						self.balance(ppl,'custom',leaderConfig,teamConfig)
							#hosterCTL[self.bid]='null'
					
					if msg.startswith("changeTeams"):
						teamConfig=' '
						teamConfig=teamConfig.join(msg.split()[1:])
						print('teamConfig:'+str(teamConfig))
#							#hosterCTL[self.bid]='null'
						self.client.sayChat('bus',self.teamAssign(teamConfig))
					
					if msg.startswith("leader") :
						leaderConfig[msg.split()[1]]=msg.split()[2]   #for every team there will be only 1 leader; every time this runs, the leader gets overwritten
					
					if msg.startswith("addAI"):
						aiList=aiList+msg.split()[1]+' '
						self.client.sayChat('bus',self.aiResponse(msg.split()[1]))
						
					if msg.startswith("killAI"):
						print('before kai'+str(aiList))
						#print('replacing'+msg.split()[1]+' ')
						aiList=aiList.replace(msg.split()[1]+' ', '')
						print('after kai'+str(aiList))
						self.client.sayChat('bus',self.kaiResponse(msg.split()[1]))

					#deliver.task_done()
				#else:   #the bid is mine, however the issuer of the cmd is not the host
					#deliver.task_done()
					#deliver.put(ctl)   #dispose of this cmd!
					#deliver.join()

				
			#if lib.quirks.hosterCTL.isInetDebug:
			#	self.client.clearBuffer(self.username)

            
#sock.close()
