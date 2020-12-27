import socket
from termcolor import colored
try:
	from multiprocessing import SimpleQueue
except:
	from queue import SimpleQueue

class Network:

	def __init__(self):
		self.cmd_queue = SimpleQueue()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		print(colored('[STCK]', 'grey'), colored('Network: Initing.', 'white'))
	def connect(self, server_ip, server_port=8200):
		self.sock.connect((server_ip, server_port))

		print(colored('[STCK]', 'grey'), colored('Network: Connecting.', 'white'))
	def send(self, cmd):
		self.sock.send(('%s\n' % cmd).encode())
		#print('Network: Send %s' % cmd)

	def receive(self):
		recvData = self.sock.recv(1024).decode("utf8").split('\n')
		for i in range(len(recvData)):
			self.cmd_queue.put(recvData[i])

	def nextCmd(self):
		return self.cmd_queue.get()

	def hasCmd(self):
		return not self.cmd_queue.empty()

	def disconnect(self):
		print("Network: Closed")
		self.sock.close()
