 
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

	def run(self):
		while True:
			self.serverNetwork.receive()
			while self.serverNetwork.hasCmd:
					# put msg in a msg queue and the hoster can import and know
				print('AUTOHOST SERVER!!!!!!!!!!!!!:'+self.serverNetwork.nextCmd)
					
