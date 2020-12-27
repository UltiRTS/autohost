import time
import threading
import os
from lib.client import Client
import _thread
import threading
from multiprocessing import Queue
from hoster import Battle #ability to open battles
from lib.quirks.autohost_factory import AutohostFactory #ability to change credential to host battles
from termcolor import colored
import lib.cmdInterpreter

#from multiprocessing import SimpleQueue

password = b'password'
map_file = 'comet_catcher_redux.sd7'
mod_file = 'Zero-K-master.sdd'
engineName = 'Spring'
engineVersion = '104.0.1-1435-g79d77ca maintenance'
mapName = 'Comet Catcher Redux'
roomName = 'Test Room'
gameName = 'Zero-K v1.8.3.5'
q = Queue()
battlePort = 2000
startDir = os.getcwd()
hosterMSGQ=["playerName","defaultAction"]



if __name__ == "__main__":

	print(colored('[INFO]', 'green'), colored('Main: Initing.', 'white'))
	client = Client(battlePort,startDir)
	autohost=AutohostFactory()
	
	client.login('Autohost_CTL',password)
	print(colored('[INFO]', 'green'), colored('Autohost_CTL: Logging in', 'white'))
	client.clearBuffer('Autohost_CTL')
	
	client.joinChat('bus')
	print(colored('[INFO]', 'green'), colored('Autohost_CTL: Joining Battle Chat.', 'white'))
	client.clearBuffer('Autohost_CTL')
	
	_thread.start_new_thread( client.keepalive,('Autohost_CTL',))
	client.clearBuffer('Autohost_CTL')
	
	gameParas = {'dataType': 'gem', 'action': 'default', 'title':'default'}
	gameTitletoBtlPtr={}
	BtlPtr=0
	battle=[]
# ,'gemType': 'default', 'isPasswded': False, 'passwd':"", 'mapFile': 'comet_catcher_redux.sd7', 'modFile': '0465683c70018f80a17b92ed78174d19.sdz', 'engineName': 'Spring', 'engineVersion': '104.0.1-1435-g79d77ca maintenance', 'mapName': 'Comet Catcher Redux', 'roomName': 'Test Room', 'gameName': 'Zero-K v1.8.3.5'
	
	while True:
		#client.ping('Autohost_CTL')
		msg=lib.cmdInterpreter.cmdRead(client.sysCTLTrigger())[1]
		#print(gameParas)
		if 'host' in msg:
					
			print("hosting")
			battle.append( Battle(msg['user'],startDir,q, autohost, password, map_file, mod_file, engineName, engineVersion, mapName,msg['host'], gameName, battlePort))  # change username, password annd room name everytime call this line
			time.sleep(1)
			battle[BtlPtr].start() #this is non blocking, the loop continues to check cmds
			gameParas['action']="default" #clear action buffer once its carried out, otherwise the same action will be done again in the next cmd
					#print('gameParas:'+gameParas['action'])
			gameTitletoBtlPtr[gameParas['title']]=BtlPtr
			BtlPtr+=1
		if 'start' in msg:
			battle[gameTitletoBtlPtr[gameParas['title']]]+=battle[gameTitletoBtlPtr[gameParas['title']]].gemStart
			battle[gameTitletoBtlPtr[gameParas['title']]].notify('start!!')
			gameParas['action']=="default"
				
					
		
	
	

	#time.sleep(10)
	#battle2 = Battle(startDir,q, autohost, password, map_file, mod_file, engineName, engineVersion, mapName, 'aaa', gameName, battlePort)  # change username, and room name everytime call this line
	#time.sleep(1)
	#battle2.start()
	
	print(colored('[INFO]', 'green'), colored('Main: Halting.', 'white'))
	time.sleep(10)

