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
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Initing.', 'white'))
	
	def bind(self, server_ip, server_port=4000):
		self.address=(server_ip, server_port)
		self.sock.bind(address)
		tcpSocket.listen(5)
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Connecting.', 'white'))
		
	def receive(self):
		while True:
			newData, newAddr=self.sock.accept()  ##keep remake connections when one client leaves
			try:
				while True:   #keep reading the next msg while the connection persists
					recvData = newData.recv(1024).decode("utf8").split('\n')
					if len(recvData) > 0:
						for i in range(len(recvData)):
							self.cmd_queue.put(recvData[i])
					else:
						print('%s客户端已经关闭' % newAddr[0])
					break
			finally:
				newData.close()
	
	def nextCmd(self):
		return self.cmd_queue.get()

	def hasCmd(self):
		return not self.cmd_queue.empty()

	def disconnect(self):
		if isInetDebug:
			print(colored('[STCK]', 'grey'), colored('Network: Closing.', 'white'))
		self.sock.close()
