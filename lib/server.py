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
		
		self.hostedby=hostedBy
		self.bid=bid
	
	def autohostInterfaceSayChat(self, msg):
		self.serverNetwork.send(msg)
	
	def run(self):
		while True:

				

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
				
				else:
					# in game chat message
					if r"\r\x00\xfe" in receivedMsg:
						#receivedMsg = receivedMsg[12:-1]
						print(colored('[INFO]', 'cyan'), "received: ", receivedMsg)
					else:
						continue
						
					ctl = {
						"bid": self.bid,
						"msg": receivedMsg,
						"caller":'Autohost',
						"ttl":0,
						"action":'sayBtlRoom'
					}
					deliver.put(ctl)
					
