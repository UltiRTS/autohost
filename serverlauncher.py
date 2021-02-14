import os

from lib.quirks.unitSync import UnitSync
class ServerLauncher():
	
	def __init__(self,startDir,battlePort,players,cmds,username,numTeams):
		self.teamPtr=0
		self.startDir=startDir
		self.battlePort=battlePort
		self.players=players
		self.cmds=cmds
		self.username=username
		self.unitSync = UnitSync(self.startDir, self.startDir+'/engine/libunitsync.so',self.username)
		self.numTeams=numTeams
	
	def scriptGen(self):
		os.system('echo [GAME] > /tmp/battle'+str(self.battlePort)+'.txt');
		os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt');
	

	##############player gen####################################
	
		#os.system('echo "NumPlayers='+str(int(len(self.players)/2))+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert number of self.players
		#print("number of self.players is "+str(int(len(self.players)/2)))

		os.system('echo \'Mapname='+str(self.unitSync.syn2map(self.cmds['map'])['mapName'].replace('🦔', ' '))+';\' >> /tmp/battle'+str(self.battlePort)+'.txt');


		for player in self.players:
			if self.players[player]['isAI']==True:
				continue
			#print("generating config for player "+player+" whose index is "+str(self.players[player]['index'])+" and in team "+str(self.players[player]['team']))
			os.system('echo "[PLAYER'+str(self.players[player]['index'])+']" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player index
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Name='+player+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player name
			os.system('echo "Spectator=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Team='+str(self.players[player]['index'])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert player team
			os.system('echo "CountryCode=??;" >> /tmp/battle'+str(self.battlePort)+'.txt'); ##ctry code
			os.system('echo "Rank=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Skill=(10);" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo } >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			
	##############AI gen############################################
		for player in self.players:
			if self.players[player]['isAI']==True:
				print("generating config for AI "+player+" whose index is "+str(self.players[player]['index'])+" and in team "+str(self.players[player]['team']))
				os.system('echo "[AI'+str(self.players[player]['index'])+']" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai index
				os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
				os.system('echo "Name=CircuitAI;" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai name
				os.system('echo "ShortName=CircuitAI;" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai name
				os.system('echo "Team='+str(self.players[player]['index'])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');   ## insert ai team
				os.system('echo "Host=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
				os.system('echo } >> /tmp/battle'+str(self.battlePort)+'.txt'); 

     ############player gen###############################################
		for player in self.players:     #for every single player, do this:
			leaderIndex=0
			for possibleLeader in self.players:
				if self.players[possibleLeader]['isLeader']==True and self.players[possibleLeader]['team']==self.players[player]['team']:    #loop through the config, find ones that's designated as leader AND in the same team as the player that's being configed ATM
					leaderIndex=self.players[possibleLeader]['index']
			
			os.system('echo "[TEAM'+str(self.teamPtr)+']" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "AllyTeam='+str(self.players[player]['team'])+';" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo "Side=Arm;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "Handicap=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "TeamLeader='+str(leaderIndex) +';" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			self.teamPtr+=1;
			
		self.teamPtr=0


	##########################TEAM GEN############################
		while self.teamPtr<self.numTeams:
			os.system('echo "[ALLYTEAM'+str(self.teamPtr)+']" >> /tmp/battle'+str(self.battlePort)+'.txt');
			os.system('echo { >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "NumAllies=0;" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			os.system('echo "}" >> /tmp/battle'+str(self.battlePort)+'.txt'); 
			self.teamPtr+=1;

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
		os.system('./engine/spring-dedicated /tmp/battle'+str(self.battlePort)+'.txt');
		#self.autohost.free_autohost(self.username)
