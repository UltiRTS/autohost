import socket
import threading
from termcolor import colored
import queue
		

## How to use
#a = AutohostServer()
#a.start()
#a.onThread(a.send, "message")


class AutohostServer(threading.Thread):
	
	def __init__(self, host='localhost', port=4000):
		threading.Thread.__init__(self)

		self.serverAddr = (host, port)
		self.q = queue.Queue()


	def onThread(self, function, *args, **kwargs):
		self.q.put((function, args, kwargs))

	def receive(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect(self.serverAddr)
		msg = self.client.recv(1024)
		self.client.close()

		return msg
	
	def send(self, msg):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if type(msg) is not bytes and type(msg) is str:
			msg = bytes(msg, encoding='utf-8')
		else:
			print(colored('[ERRO]', 'red'), 'The msg send to spring engine is wrong format')
			return

		try:
			self.client.connect(self.serverAddr)
			need2send = len(msg)
			real2send = self.client.send(msg)

			if need2send != real2send:
				print(colored('[WARN]', 'red'), 'msg not sent completely.')
		except Exception as e:
			print(colored('[ERRO]', 'red'), 'error at autohostServer: ', str(e))
			self.client.close()
			return
		finally:
			self.client.close()


		print(colored('[INFO]', 'white'), 'message sent to spring engine: ', str(msg))
	
	def idle(self):
		# something originally put in run
		pass
	
	def run(self):
		while True:
			try:
				# executes all instuctions in q
				function, args, kwargs = self.q.get(timeout=1)
				print(args, kwargs)
				function(*args, **kwargs)
			except queue.Empty:
				self.idle()	

