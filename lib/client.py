from base64 import b64encode
from hashlib import md5
from lib.quirks.network import Network
from lib.quirks.unitSync import UnitSync
from serverlauncher import ServerLauncher
from termcolor import colored
import lib.quirks.hosterCTL

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
				return chatBuffer
		return "Probably not a cmd line!"


	def login(self, username,password, local_ip='*', cpu=0):
		password = b64encode(md5(password).digest()).decode('utf8')
		command = 'LOGIN %s %s %i %s' % (username, password, cpu, local_ip)
		self.network.send(command)



	def openBattle(self, battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name):
		self.network.receive()
		command = 'OPENBATTLE %i %i %s %i %i %i %i %i %s\t%s\t%s\t%s\t%s' % (battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name)
		self.network.send(command)
		while True:
			self.network.receive()
			while self.network.hasCmd():
				response=self.network.nextCmd()
				if 'BATTLEOPENED' in response:
					return response.split()[1]




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
				if lib.quirks.hosterCTL.isInetDebug:
					print(colored('[INET]', 'grey'), colored(username+': keeping alive', 'white'))
				time.sleep(10)
			except:
				return;

	def ping(self,username):
		command = 'PING'
		self.network.send(command)
	
	
	def joinChat(self, channel):

		command = 'JOIN '+channel
		self.network.send(command)
		

	def exit(self):
		self.network.disconnect()

	def clearBuffer(self, username):
		self.network.receive()	
		while(self.network.hasCmd()):
			#self.network.nextCmd()
			if lib.quirks.hosterCTL.isInetDebug:
				print(colored('[INET]', 'grey'), colored(username+': '+self.network.nextCmd(), 'white'))
			else:
				self.network.nextCmd()

