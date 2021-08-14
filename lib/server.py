import threading
from termcolor import colored
from lib.quirks.serverNetwork import serverNetwork


import re
import struct


chatMsgPatt = re.compile(r".*\\r\\x[0-9]{2}\\xfe")


class AutohostServer(threading.Thread):

	def __init__(self, host, port, hostedBy, bid, deliver, username):
		threading.Thread.__init__(self)
		self.serverNetwork = serverNetwork()
		self.serverNetwork.bind(host, port)
		self.username = username
		self.hostedby = hostedBy
		self.bid = bid
		self.deliver = deliver

	def autohostInterfaceSayChat(self, msg):
		self.serverNetwork.send(msg)


		
	def decode(self, buf):
		unpacked=(-1,)
		if not buf:
			return unpacked
		
		elif buf[0]==bytes([0])[0]:
			#return unpacked #you dont
			print('serverstarted')
			print(buf)
			unpacked = struct.unpack('B',buf)
			#print(str(unpacked))
		elif buf[0]==bytes([1])[0]:
			#return unpacked
			print('QuitMsg!')
			unpacked = struct.unpack('B',buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([2])[0]:
			print('startMsg!')
			#return unpacked #you dont
			#print(buf)
			unpacked = struct.unpack('=BI16B{}s'.format(len(buf)-struct.calcsize('=BI16B')),buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([3])[0]:
			print('gameOverMsg!')
			unpacked = struct.unpack('BBB{}B'.format(len(buf)-struct.calcsize('BBB')),buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([10])[0]:
			print('joinMsg!')
			unpacked = struct.unpack('BB{}s'.format(len(buf)-struct.calcsize('BB')),buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([11])[0]:
			print('leftMsg!')
			unpacked = struct.unpack('BBB',buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([12])[0]:
			print('readyMsg!')
			#print(buf)
			unpacked = struct.unpack('BBB',buf)
			#except:
				#unpacked = struct.unpack('B',buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([13])[0]:
			print('chatMsg!')
			unpacked = struct.unpack('BBB{}s'.format(len(buf)-struct.calcsize('BBB')),buf)
			print(str(unpacked))
			
		elif buf[0]==bytes([14])[0]:
			print('defeatMsg!')
			unpacked = struct.unpack('BB',buf)
			print(str(unpacked))
		
		if buf[0]==bytes([20])[0]:
			return unpacked #you dont
			#print('luaMsg!')
			#unpacked = struct.unpack('BHB{}s'.format(len(buf)-struct.calcsize('BHB')),buf)
			#print(unpacked)
			
		
			
		
			
		
			
		
			
		
			
		elif buf[0]==bytes([5])[0]:
			print('warnMsg!')
			unpacked = struct.unpack('B{}s'.format(len(buf)-struct.calcsize('B')),buf)
			print(str(unpacked))
			
		#elif buf.startswith(bytes([4])):    //functional, but useless
			#print('serverMsg!')
			#unpacked = struct.unpack('B{}s'.format(len(buf)-struct.calcsize('B')),buf)
			#print(str(unpacked))
			
		
			
		
			
		
			
		
		return unpacked
	

	def run(self):
		while True:

			self.serverNetwork.receive()
			while self.serverNetwork.hasCmd():
				# print('autohost server interface triggered')

				receivedMsg = self.serverNetwork.nextCmd()
				interfaceDecoded=self.decode(receivedMsg)
				# print('AUTOHOST SERVER!!!!!!!!!!!!!:'+str(self.serverNetwork.nextCmd()))
				#print(interfaceDecoded)
				if interfaceDecoded[0]==1:
					ctl = {
						"bid": self.bid,
						"msg": 'exit',
						"caller": self.hostedby,
						"action": 'exit'}
					self.deliver.put(ctl)
					return
					#print(colored('[INFO]', 'cyan'), receivedMsg)
					
				
					
				if interfaceDecoded[0]==13:
					

					ctl = {
						"bid": self.bid,
						"msg": interfaceDecoded[3].decode('utf-8'),
						"caller": interfaceDecoded[1],
						"action": 'sayBtlRoom'
					}
					self.deliver.put(ctl)

