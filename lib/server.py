import threading
from termcolor import colored
from lib.quirks.serverNetwork import serverNetwork
import chardet
import ctypes


#import re
#import struct


#chatMsgPatt = re.compile(r".*\\r\\x[0-9]{2}\\xfe")


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

	def decode(self,buf:bytearray):
		try:
			header = buf[0]
			body = buf[1:]
		except: #the server sent an message thats either empty or doesnt have a body
			return

		# server started
		if header == 0:
			return {
				"type": "server-started",
			}
		# server is about to exit
		if header == 1:
			return {
				"type": "server-to-exit",
			}
		# game starts
		if header == 2:
			return {
				"type": "game-starts",
			}
		# game has ended
		if header == 3:
			return {
				"type": "game-ended",
			}
		# an information message from server (string message)
		if header == 4:
			return {
				"type": "server-msg",
				"msg": body.decode(encoding='UTF-8',errors='ignore')

			}
		# Server gave out a warning (string warning message)
		if header == 5:
			return {
				"type": "server-warn",
				"msg": body.decode(encoding='UTF-8',errors='ignore')

			}
		# player has joined the game (uchar playernumber, string name)
		if header == 10:
			class Info(ctypes.Structure):
				_fields_ = [('playernumber', ctypes.c_uint8),
							('name', ctypes.c_uint8 * (len(body) - 1))]
			
			info = Info.from_buffer(body)
			return {
				"type": "game-join",
				"playernumber": info.playernumber,
				"name": info.name.decode(encoding='UTF-8',errors='ignore')

			}
		# player has left (uchar playernumber, uchar reson)
		# (0: lost connection, 1: left, 2: kicked)
		if header == 11:
			class Info(ctypes.Structure):
				_fields_ = [('playernumber', ctypes.c_uint8),
							('reason', ctypes.c_uint8)]
				
				def Reason(self):
					if self.reason == 0:
						return 'lost connection'
					if self.reason == 1:
						return 'left'
					if self.reason == 2:
						return 'kicked'

			info = Info.from_buffer(body)
			return {
				'type': 'left',
				'reason': info.Reason()
			}
		# player has updated its ready-state
		# (uchar playernumber, uchar state)
		# (0: not ready, 1: ready, 2: state not changed)
		if header == 12:
			class Info(ctypes.Structure):
				_fields_ = [('playernumber', ctypes.c_uint8),
							('ready_state', ctypes.c_uint8)]

				def readyState(self):
					if self.ready_state == 0:
						return 'not ready'
					if self.ready_state == 1:
						return 'ready'
					if self.ready_state == 2:
						return 'state not changed'
				
			info = Info.from_buffer(body)
			return {
				"type": "ready-state",
				"playernumber": info.playernumber,
				"ready_state": info.readyState(),
			}

		# player has sent a chat message
		# (uchar playernumber, uchar destination, string text)
		# Destination can be any of: a playernumber [0-32]
		# static const int TO_ALIES = 127
		# static const int TO_SPECTATORS = 126
		# static const int TO_EVERYONE = 125
		if header == 13:
			class Info(ctypes.Structure):
				_fields_ = [('playernumber', ctypes.c_uint8),
							('destination', ctypes.c_uint8),
							('text', ctypes.c_char * (len(body) - 2))]
				
				def Destination(self):
					print(self.destination)
					#if self.destination == 127:
						#return 'To allies'
					#if self.destination == 126:
						#return 'To spectators'
					if self.destination == 254:
						return 'everyone'
					
					return self.destination

			info = Info.from_buffer(body)		
			return {
				'type': 'chat',
				'destination': info.Destination(),
				'playerNum':info.playernumber,
				'msg': info.text.decode('utf-8'),
			}
		# player has been defeated (uchar playernumber)
		if header == 14:
			playernumber = ctypes.c_uint8(body)
			return {
				'type': 'defeat',
				'playernumber': int(playernumber)
			}
		# brief message sent by lua script
		# (uchar playernumber, uint16_t script, uint8_t mode, uint8_t[X] data)
		# (X = space left in packet)
		if header == 20:
			return #FIXME:  ValueError: Buffer size too small (33 instead of at least 34 bytes)
 
			class Info(ctypes.Structure):
				_fields_ = [("playernumber", ctypes.c_uint8),
							("script", ctypes.c_uint16),
							("mode", ctypes.c_uint8),
							("data", ctypes.c_uint8 * (len(body) - 3)),]
			
	#		if ctypes.sizeof(Info) != len(body):
	#			raise Exception("Can't conversion except {} but got {}".format(ctypes.sizeof(Info), len(body)))

	#		info = Info.from_buffer(body)
			info = Info.from_buffer(body)

			return {
				"type": "lua-script",
				"playernumber": info.playernumber,
				"script": info.script,
				"mode": info.mode,
				"data": info.data,
			}

	def run(self):
		while True:

			self.serverNetwork.receive()
			while self.serverNetwork.hasCmd():
				#print('autohost server interface triggered')

				receivedMsg = self.serverNetwork.nextCmd()
				#print('AUTOHOST SERVER!!!!!!!!!!!!!:'+str(self.serverNetwork.nextCmd()))
				res = self.decode(bytearray(receivedMsg))
				if res==None:
					continue
				print(res)
				if b'No clients connected, shutting down server' in receivedMsg:
					ctl = {
						"bid": self.bid,
						"msg": 'exit',
						"caller": self.hostedby,
						"action": 'exit'}
					self.deliver.put(ctl)

				if res['type']=='chat' and res['destination']=='everyone':

					ctl = {
						"bid": self.bid,
						"msg": res['msg'],
						"caller": res['playerNum'],
						
						"action": 'sayBtlRoom'
					}
					self.deliver.put(ctl)

#chatMsgPatt