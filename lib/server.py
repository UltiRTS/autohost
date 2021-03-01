 
import socket
import threading
from termcolor import colored
from lib.quirks.serverNetwork import serverNetwork
import queue

deliver = queue.Queue()




class AutohostServer(threading.Thread):

	def __init__(self, host='0.0.0.0', port=4000):
		threading.Thread.__init__(self)
		self.serverNetwork=serverNetwork()
		self.serverNetwork.bind(host,port)
		self.q = queue.Queue()
	
	def msgSendOnThread(self, msg):
		self.q.put(msg)
	
	def run(self):
		while True:
			# not adding to a while loop
			while not self.q.empty():
				msg = self.q.get()
				self.serverNetwork.send(msg)

			self.serverNetwork.receive()
			while self.serverNetwork.hasCmd():
					# put msg in a msg queue and the hoster can import and know
				print('AUTOHOST SERVER!!!!!!!!!!!!!:'+str(self.serverNetwork.nextCmd()))
					
