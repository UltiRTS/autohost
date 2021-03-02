 
import socket
import threading
from termcolor import colored
from lib.quirks.serverNetwork import serverNetwork
import queue

deliver = queue.Queue()




class AutohostServer(threading.Thread):

	def __init__(self, host, port,hostedBy,bid):
		threading.Thread.__init__(self)
		self.serverNetwork=serverNetwork()
		self.serverNetwork.bind(host,port)
		self.q = queue.Queue()
		self.hostedby=hostedBy
		self.bid=bid
	
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
				receivedMsg=self.serverNetwork.nextCmd()
				#print('AUTOHOST SERVER!!!!!!!!!!!!!:'+str(self.serverNetwork.nextCmd()))
				if 'No clients connected, shutting down server' in receivedMsg:
					ctl = {
						"bid": self.bid,
						"msg": 'exit',
						"caller":self.hostedby,
						"ttl":0,
						"action":'exit'
					}
					deliver.put(ctl)
					
