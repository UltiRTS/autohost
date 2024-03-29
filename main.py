#from lib.message_queue import Deliver
import os
from lib.client import Client
import _thread

from hoster import Battle #ability to open battles
from lib.quirks.autohost_factory import AutohostFactory #ability to change credential to host battles
from termcolor import colored
import lib.cmdInterpreter
from lib.quirks.hosterCTL import isInetDebug
from lib.quirks.hosterCTL import hosterPool
#from multiprocessing import SimpleQueue
password = b'password'
map_file = 'Comet'
mod_file = 'mod.sdd'
engineName = 'Spring'
engineVersion = '104.0.1-1435-g79d77ca maintenance'
gameName = 'Zero-K v1.8.3.5'

battlePort = 2000
startDir = os.getcwd()


#lib.quirks.hosterCTL.isInetDebug=True   #turn true to enable network msg inspection

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


	

	BtlPtr=0
	battle=[]
	
# ,'gemType': 'default', 'isPasswded': False, 'passwd':"", 'mapFile': 'comet_catcher_redux.sd7', 'modFile': '0465683c70018f80a17b92ed78174d19.sdz', 'engineName': 'Spring', 'engineVersion': '104.0.1-1435-g79d77ca maintenance', 'mapName': 'Comet Catcher Redux', 'roomName': 'Test Room', 'gameName': 'Zero-K v1.8.3.5'
	
	while True:

		#client.ping('Autohost_CTL')
		servermsg=client.sysCTLTrigger()
		user=servermsg.split()[2]
		msg=lib.cmdInterpreter.cmdRead(servermsg[3:])[1]
		hoster=0

		#print(servermsg)
		
		###COMMANDS BELOW ARE HOST ONLY. NON POLLABLE. HOSTER NOT EXECUTING IF THOSE ARE NOT GENERATED BY HOST#############
		###The logic of the interpreter is that the main ctl code grabs any ctl command and associates them with the battle id they were coming from. hoster periodically checks the bid associated commands in the dictionary. If such commands exist, hoster checks the issuer. If the issuer isn't the host, it is discarded.
		if 'host' in msg:
			hosterPool.append( Battle(msg['user'],startDir, autohost, password, map_file, mod_file, engineName, engineVersion, msg['title'], gameName, 2000+BtlPtr,client))  # change username, password annd room name everytime call this line
			hosterPool[BtlPtr].start() #this is non blocking, the loop continues to check cmds
			
			BtlPtr+=1
			
		else:
			# adding the ctl to Message queue, when all ctl been got and processed, the `hoster.py` call task_done then back to `main.py` to move to next command
			try:   #get rid or any message that contains neither bid in their protocol or bid in their command (continue to the next loop)
				while hoster < len(hosterPool):
					if str(hosterPool[hoster].bid) == str(msg['bid']) and not hosterPool[hoster].bid==-1:
						break
					hoster+=1
				else:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Dropping msg with bid(cmd)'+str(msg['bid']), 'white'))
					continue
			except Exception as e:     #this is for msg relay purpose
				hoster=0
				while hoster < len(hosterPool):
					if str(servermsg.split()[2])==str(hosterPool[hoster].bid) and not hosterPool[hoster].bid==-1:
						break
					hoster+=1
				else:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Dropping msg with bid (relay msg)'+str(servermsg.split()[2])+str(e), 'white'))
					continue	
		
			if servermsg.startswith('msgRelay'):    #this shouldnt go into the interpreter!!
				bid=servermsg.split()[2]
				user=servermsg.split()[3]
				msg=servermsg.split()[4:]
				ctl = {
						"bid": bid,
						"msg": ' '.join(msg),
						"caller":user,
						
						"action":'forward2AutohostInterface'
					}
				hosterPool[hoster].deliver.put(ctl)
				print('msgRelay sending'+str(ctl))
				continue
			
			if 'spec' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": user,
						"caller":user,
						
						"action":'specOrder'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete SpecOrder cmd', 'white'))
			
			if 'despec' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": user,
						"caller":user,
						
						"action":'despecOrder'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete SpecOrder cmd', 'white'))
			
			if 'joinasSpec' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": 'joinasSpec',
						"caller":user,
						
						"action":'joinasSpec'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete joinasSpec cmd', 'white'))

			if 'comment' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": msg['comment'],
						"caller":user,
						
						"action":'comment'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete comment cmd', 'white'))
			
			if 'cheat' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": 'cheat',
						"caller":user,
						
						"action":'cheat'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete cheat cmd', 'white'))

			if 'exit' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": 'exit',
						"caller":user,
						
						"action":'exit'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete exit cmd', 'white'))

			if 'map' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": msg['map'],
						"caller":user,
						
						"action":'chmap'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete chmap cmd', 'white'))
					
				#print('satisfying chmap from main')
			if 'leave' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": user,
						"caller":user,
						
						"action":'left'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete leave cmd', 'white'))
				
			if 'start' in msg:
				try:
					ctl = {
						"bid": msg['bid'],
						"msg": user,
						"caller":user,
						
						"action":'start'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete start cmd', 'white'))
				
				
			if 'leader' in msg:
				try:
					ctl = {
					"bid": msg['bid'],
					"msg":"leader "+msg['leader'],
					"caller":user,
					
					"action":'leader'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete leader cmd', 'white'))
				
				
			if 'player' in msg:
				try:
					ctl = {
					"bid": msg['bid'],
					"msg": msg['player'],
					"caller":user,
					
					"action":'teams'
					}
					hosterPool[hoster].deliver.put(ctl)
				except:
					print(colored('[WARN]', 'red'), colored('Autohost_CTL: Incomplete player cmd', 'white'))
			


