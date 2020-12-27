import os
import fnmatch
import libarchive
from libarchive import file_reader
class ServerLauncher():
	
	def __init__(self,startDir,battlePort,players,ais,cmds,username,autohost):
		
		self.startDir=startDir
		self.battlePort=battlePort
		self.players=players
		self.ais=ais
		self.cmds=cmds
		self.username=username
		self.autohost=autohost
	def syn2map(self,filename):
		files= os.listdir(self.startDir+'/engine/maps')
		for file in files:
			if fnmatch.fnmatch(file, filename):
				print("Actual Mapname="+file);
				with libarchive.file_reader(self.startDir+'/engine/maps/'+file) as reader:
					for e in reader:
					# (The entry evaluates to a filename.)
						print(e)
						if e.name[-3:]=='smf' :
							print("real map name: "+e.name)
							filename=e.name
							break;
				break;
		print("returning name"+ filename[5:-4])
		return filename[5:-4]
	
	def scriptGen(self):
		os.system('echo [GAME] > /tmp/battle'+str(self.battlePort)+'.txt');
		os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt');
	
		filename= 'null'
		cmdPtr=0;
		playerPtr=0;
		AIPtr=0;
		maxTeam=0;
		teamPtr=0;
	###################cmd interpreter loop####################
		while cmdPtr<len(self.cmds):
			cmdPtr+=2;
		#########MAP SELECTOR MODULE###############################
			if self.cmds[cmdPtr-2]== "map":
			
				print("looking for file Mapname="+self.cmds[cmdPtr-1]);
			
				os.system('echo "Mapname='+self.syn2map(self.cmds[cmdPtr-1])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');
	##############player gen####################################
	
		os.system('echo "NumPlayers='+str(int(len(self.players)/2))+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert number of self.players
		print("number of self.players is "+str(int(len(self.players)/2)))



		while playerPtr<len(self.players):
			playerPtr+=2;
			print("generating config for player "+str(self.players[playerPtr-2])+" whose index is "+str(int(playerPtr/2)-1)+" and in team "+str(int(self.players[playerPtr-1])))
			os.system('echo "[PLAYER'+str(int(playerPtr/2)-1)+']" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player index
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Name='+str(self.players[playerPtr-2])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player name
			os.system('echo "Spectator=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Team='+str(int(self.players[playerPtr-1]))+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player team
			os.system('echo "CountryCode=??;" >> /tmp/battle'+str(self.battlePort)+'.txt'); ##ctry code
			os.system('echo "Rank=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "AccountId='+str(int(playerPtr/2)-1)+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player id
			os.system('echo "Skill=(10);" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo } >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			if self.players[playerPtr-1] > maxTeam:
				maxTeam=self.players[playerPtr-1]
	##############AI gen############################################
		while AIPtr<len(self.ais):
			AIPtr+=2;
			print("generating config for AI "+str(self.ais[AIPtr-2])+" whose index is "+str(int(AIPtr/2)-1)+" and in team "+str(int(self.ais[AIPtr-1])))
			os.system('echo "[AI'+str(int(playerPtr/2)-1)+']" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai index
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Name='+str(self.ais[AIPtr-2])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai name
			os.system('echo "ShortName='+str(self.ais[AIPtr-2])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai name
			os.system('echo "Team='+str(int(self.ais[AIPtr-1]))+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai team
			os.system('echo "Host=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo } >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			if self.ais[AIPtr-1] > maxTeam:
				maxTeam=self.ais[AIPtr-1]
	
		os.system('echo "NumTeams='+str(int(maxTeam)+1)+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert number of self.players
		print("number of teams is "+str(int(maxTeam)+1))

		os.system('echo "NumAllyTeams='+str(int(maxTeam)+1)+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert number of self.players
		print("number of NumAllyTeams is "+str(int(maxTeam)+1))

	##########################TEAM GEN############################
		while teamPtr<=maxTeam:
			teamPtr+=1;
			print("Generating config for TEAM "+str(int(teamPtr-1))+" and ally team "+str(int(teamPtr-1)))
			os.system('echo "[TEAM'+str(int(teamPtr-1))+']" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "AllyTeam='+str(int(teamPtr-1))+';" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo "Side=Robots;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Handicap=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "TeamLeader=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "[ALLYTEAM'+str(int(teamPtr-1))+']" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "NumAllies=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt'); 

	#########NON-user set SETTINGS ARE OUT OF THE INTERPRETER LOOP
	#########GAME SELECTOR MODULE###############################	
		os.system('echo "Gametype=Zero-K-master.sdd;" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## for now it's just zk, extend when we have our own game
		print("game type is zk")
	
	#########startposi selector MODULE###############################	
		os.system('echo "startpostype=2;" >> /tmp/battle'+str(self.battlePort)+'.txt');   
		print("start position is   startpostype=2;")###IDK what this module does
	
	#########autohost ident MODULE###############################	
		os.system('echo "hosttype=SPADS;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		print("autohost is   hosttype=SPADS;")###IDK what this module does
	
	#########autohost ip MODULE###############################	
		os.system('echo "HostIP=;" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		print("AUTOHOST IP is HostIP=;")###IDK what this module does
	
	#########host port MODULE###############################	
		os.system('echo "HostPort='+str(self.battlePort)+';" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		print("HOST port is "+str(self.battlePort))###IDK what this module does		
	
	#########autohost usr MODULE###############################	
		os.system('echo "AutoHostName=GGFrog;" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		os.system('echo "AutoHostCountryCode=??;" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		os.system('echo "AutoHostRank=1;" >> /tmp/battle'+str(self.battlePort)+'.txt');
		os.system('echo "AutoHostAccountId=1024;" >> /tmp/battle'+str(self.battlePort)+'.txt');
		os.system('echo "IsHost=1;" >> /tmp/battle'+str(self.battlePort)+'.txt');

	#########autohost port MODULE###############################	
		os.system('echo "AutohostPort='+str(2000+self.battlePort)+';" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		print("AUTOHOST port is "+str(2000+self.battlePort))###IDK what this module does

	########RESTRICTION GEN########################################	
		os.system('echo "NumRestrictions=0;" >> /tmp/battle'+str(self.battlePort)+'.txt');  
		print("AUTOHOST NumRestrictions=0;")###IDK what this module does		
		os.system('echo [RESTRICT] >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt');	

	##########MOD OPTIONGEN################################################
		os.system('echo [MODOPTIONS] >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt');

	##########MAP OPTIONGEN################################################
		os.system('echo [MAPOPTIONS] >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
		os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt');
		os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt');
		

	def launch(self):
		os.system('./spring-dedicated /tmp/battle'+str(self.battlePort)+'.txt');
		self.autohost.free_autohost(self.username)
