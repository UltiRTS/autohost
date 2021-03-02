import os
import socket
from termcolor import colored
from lib.quirks.hosterCTL import isInetDebug
import time

try:
	from multiprocessing import SimpleQueue
except:
	from queue import SimpleQueue

class serverNetwork:

	def __init__(self):
		self.cmd_queue = SimpleQueue()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('SERVER Network: Initing.', 'white'))
	
	def bind(self, server_ip, server_port=4000):
		self.address=(server_ip, server_port)
		self.sock.bind(self.address)
		#self.sock.listen(5)
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('SERVER Network: Connecting.', 'white'))
		
	def send(self, command):
		if type(command) is not str:
			return

		#try:
		self.sock.sendto(command.encode('utf8'),self.newAddr)
		#except:
			#print(colored('[ERRO]', 'red'), 'failed to send command to engine')

	def receive(self):
		newData, self.newAddr=self.sock.recvfrom(1024)  ##keep remaking connections when one client leaves

		#if not os.path.exists("recv.txt"):
			#with open("recv.txt", 'w') as f:
				#f.write(str(newData) + '\n')
		#else:
			#with open("recv.txt", 'a') as f:
				#f.write(str(newData) + '\n')

		
		try:
			recvData = newData.decode("utf8").split('\n')
			
			if len(recvData) > 0:
				for i in range(len(recvData)):
					self.cmd_queue.put(recvData[i])
			else:
				print('%sconnection closed' % newAddr[0])
		except:
			return
		
		#finally:
			#newData.close()
	
	def nextCmd(self):
		return self.cmd_queue.get()

	def hasCmd(self):
		return not self.cmd_queue.empty()

	def disconnect(self):
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Server Network: Closing.', 'white'))
		self.sock.close()
