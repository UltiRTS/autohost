import socket
from termcolor import colored
from lib.quirks.hosterCTL import isInetDebug

try:
	from multiprocessing import SimpleQueue
except:
	from queue import SimpleQueue

class Network:

	def __init__(self):
		self.cmd_queue = SimpleQueue()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Initing.', 'white'))
	def connect(self, server_ip, server_port=8200):
		self.sock.connect((server_ip, server_port))
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Connecting.', 'white'))
	def send(self, cmd):
		self.sock.send(('%s\n' % cmd).encode())
		#print('Network: Send %s' % cmd)

	def receive(self):
		recvData = self.sock.recv(1024).decode("utf8", 'ignore')
		#recvData = self.sock.recv(1024)
		#print(recvData)
		while not recvData.endswith('\n'):
			recvData+=self.sock.recv(1024).decode("utf8")
		
		recvData=recvData.split('\n')
		for i in range(len(recvData)):
			self.cmd_queue.put(recvData[i])

	def nextCmd(self):
		return self.cmd_queue.get()

	def hasCmd(self):
		return not self.cmd_queue.empty()

	def disconnect(self):
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Closing.', 'white'))
		self.sock.close()
