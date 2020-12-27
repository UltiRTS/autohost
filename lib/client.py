from base64 import b64encode
from hashlib import md5
from lib.quirks.network import Network
from lib.quirks.unitSync import UnitSync
from serverlauncher import ServerLauncher
from termcolor import colored
import time



class Client():

	def __init__(self, battlePort, startDir):
		
		self.network = Network()
		self.network.connect('ultirts.net')
		self.battlePort=battlePort
		self.startDir=startDir
	
	def sysCTLTrigger(self):
		
		self.network.receive()
		
		#return "word to split"
		while self.network.hasCmd():
			
			#print("aaanetwork has cmd!")
			chatBuffer=self.network.nextCmd()
			
			#print(chatBuffer)
			#self.network.receive()
			if 'sysctl' in chatBuffer:
				print("trigger running"+chatBuffer)
				return "sysctl "+chatBuffer.split("sysctl",1)[1] 
				
			
		return "Probably not a cmd line!"


	def login(self, username,password, local_ip='*', cpu=0):
		password = b64encode(md5(password).digest()).decode('utf8')
		command = 'LOGIN %s %s %i %s' % (username, password, cpu, local_ip)
		self.network.send(command)



	def openBattle(self, battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name):
		command = 'OPENBATTLE %i %i %s %i %i %i %i %i %s\t%s\t%s\t%s\t%s' % (battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name)
		self.network.send(command)


	def startBattle(self):
		time.sleep(2)
		command = 'MYSTATUS 1'
		self.network.send(command)


	def keepalive(self,username):
		
		command = 'PING'
		self.network.send(command)
		

		while (True):
			try:
				self.network.send(command)
				print(colored('[INET]', 'grey'), colored(username+': keeping alive', 'white'))
				time.sleep(5)
			except:
				return;
	def ping(self,username):
		
		command = 'PING'
		self.network.send(command)
	
	
	def joinChat(self, channel):
		print('joining')
		command = 'JOIN '+channel
		self.network.send(command)
		
	def hostPresence(self, host, gameID):
		#print('pre receive')
		self.network.receive()
		#print('post receive')
		while self.network.hasCmd():
			#print("network has cmd!")
			chatBuffer=self.network.nextCmd()
			#print('check host')
			#print(host)
			#print('host cmd')
			#print(chatBuffer)
			#self.network.receive()
			if 'LEFT' in chatBuffer and host in chatBuffer and gameID in chatBuffer:
				print("host left!")
				return False

	
	def battleOpenInfo(self,username):
			self.network.receive()
			#print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!binfo called'+str(self.network.hasCmd()))
			#
			self.network.receive()
			while True:
				
				#print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!binfo called')
				chatBuffer=self.network.nextCmd()
				#print("network has cmd! checking for"+ username)
				#print(chatBuffer)
			#print(chatBuffer)
			#self.network.receive()
				if 'BATTLEOPENED' in chatBuffer and username in chatBuffer:
					#print("returning "+chatBuffer)
					return chatBuffer

	def exit(self):
		self.network.disconnect()

	def clearBuffer(self, username):
		self.network.receive()	
		while(self.network.hasCmd()):
			#self.network.nextCmd()
			print(colored('[INET]', 'grey'), colored(username+': '+self.network.nextCmd(), 'white'))

