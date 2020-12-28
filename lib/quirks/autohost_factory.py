import time
from multiprocessing import SimpleQueue
from lib.quirks.network import Network
from base64 import b64encode
from hashlib import md5
from termcolor import colored
class AutohostFactory:

	def __init__(self):
		
		self.idlehosts = SimpleQueue()
		self.count = 0
		self._load_autohosts()

	def new_autohost(self):

		print(colored('[INFO]', 'green'), colored('AFAC: Initing.', 'white'))
		if self.idlehosts.empty():
			username = self._new_autohost()
			print(colored('[INFO]', 'green'), colored('AFAC: Registering'+ username+'.', 'white'))
			return username
		else:
			username=self.idlehosts.get()

			print(colored('[INFO]', 'green'), colored('AFAC: Returning spare username:'+ username+'.', 'white'))
			return username
		

	def free_autohost(self, username):
		self.idlehosts.put(username)

		print(colored('[INFO]', 'green'), colored('AFAC: Returning'+ username+'to the idle pool.', 'white'))
	def _new_autohost(self):
		network = Network()
		network.connect('ultirts.net')
		username = "Autohost_%i" % self.count
		password = b64encode(md5(b'password').digest()).decode('utf8')
		network.send("REGISTER %s %s" % (username, password)) # TODO: Check for errors
		network.disconnect()
		network = Network()
		network.connect('ultirts.net')
		command = 'LOGIN %s %s %i %s' % (username, password, 0, '*')
		network.send(command)
		print(colored('[WARN]', 'red'), colored('AFAC: registering new account '+username, 'white'))
		network.send("CONFIRMAGREEMENT")
		network.receive()
		while network.hasCmd():
			network.nextCmd()
		self._save_autohost(username)
		
		self.count += 1
		return username

	def _load_autohosts(self):
		with open('autohosts.txt', 'r') as file:
			usernames = file.read().split('\n')
			for username in usernames:
				if username != '':
					
					print(colored('[INFO]', 'green'), colored('AFAC: added.'+username, 'white'))
					self.idlehosts.put(username)
					self.count += 1

	def _save_autohost(self, username):
		with open('autohosts.txt', 'a') as file:
			file.write('%s\n' % username)
