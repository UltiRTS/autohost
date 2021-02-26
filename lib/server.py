 
import socket
import threading
from termcolor import colored
from lib.quirks.network import serverNetwork
import queue


## How to use
#a = AutohostServer()
#a.start()
#a.onThread(a.send, "message")


class AutohostServer(threading.Thread):

	def __init__(self, host='localhost', port=4000):
		threading.Thread.__init__(self)
		self.serverNetwork=serverNetwork
		self.serverNetwork.bind()

	def run(self):
		while True:
			self.serverNetwork.receive()
				while self.serverNetwork.hasCmd:
					# put msg in a msg queue and the hoster can import and know
					# msgq= self.serverNetwork.nextCmd
					
