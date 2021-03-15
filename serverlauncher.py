import os

from lib.quirks.unitSync import UnitSync
import subprocess


class ServerLauncher():
	
	def __init__(self):
		self.teamPtr=0
		
		
		
		

		# using subprocess to invoke spring engine
		
	
	def scriptGen(self,startDir,battlePort,players,cmds,username,numTeams):
		self.startDir=startDir
		self.battlePort=battlePort
		self.players=players
		self.cmds=cmds
		self.username=username
		self.numTeams=numTeams
		self.unitSync = UnitSync(self.startDir, self.startDir+'/engine/libunitsync.so',self.username)

		

		game = OptionFactory('GAME')


		game.addFromDict({
			'Mapname':  str(self.unitSync.syn2map(self.cmds['map'])['mapName'].replace('🦔', ' '))
			})


	##############player gen####################################
		for player in self.players:
			if self.players[player]['isAI']==True:
				continue


			pl = OptionFactory("PLAYER" + str(self.players[player]['index']))
			pl.addFromDict({
				'Name': player,
				'Spectator': 0,
				'Team': self.players[player]['index'],
				'CountryCode': "??",
				'Rank': 0,
				'Skill': "(10)"
				})

			game.addFromOptionInstance(pl)


	##############AI gen############################################
		defaultLeader = None
		for player in self.players:
			if self.players[player]['isLeader']:
				defaultLeader = self.players[player]['index']
				break
		
		if defaultLeader is None:
			defaultLeader = 0
			
		for player in self.players:
			if self.players[player]['isAI']==True:
				ai = OptionFactory("AI" + str(self.players[player]['index']))
				ai.addFromDict({
					'ShortName': 'CircuitAI',
					'Name': 'CircuitAI',
					'Team': self.players[player]['index'],
					'Host': defaultLeader,
				})
				game.addFromOptionInstance(ai)
			elif self.players[player]['isChicken']==True:
				ai = OptionFactory("AI" + str(self.players[player]['index']))
				ai.addFromDict({
					'ShortName': 'Chicken: Suicidal',
					'Name': 'AI: Chicken: Suicidal',
					'Team': self.players[player]['index'],
					'Host': defaultLeader,
				})
				game.addFromOptionInstance(ai)
				

		

		

     ############player gen###############################################
		for player in self.players:     #for every single player, do this:
#			leaderIndex=0
#			for possibleLeader in self.players:
#				if self.players[possibleLeader]['isLeader']==True and self.players[possibleLeader]['team']==self.players[player]['team']:    #loop through the config, find ones that's designated as leader AND in the same team as the player that's being configed ATM
#					leaderIndex=self.players[possibleLeader]['index']
#			if self.players[player]['isAI']==True:
#				continue
			
			if self.players[player]['isAI'] == True:
				team = OptionFactory("TEAM" + str(self.teamPtr))
				team.addFromDict({
					'AllyTeam': self.players[player]['team'],
					'Side':'Arm',
					'Handicap':0,
					'TeamLeader': defaultLeader
				})
				game.addFromOptionInstance(team)
			else:
				team = OptionFactory("TEAM" + str(self.teamPtr))
				team.addFromDict({
					'AllyTeam': self.players[player]['team'],
					'Side':'Arm',
					'Handicap':0,
					# The player itself is leader
					'TeamLeader': self.players[player]['index']
				})
				game.addFromOptionInstance(team)
				

#			if self.players[player]['isAI']==True:
#				team.addFromDict({'TeamLeader': leaderIndex})
#			else:
#				team.addFromDict({'TeamLeader': self.players[player]['index']})
				
			self.teamPtr+=1;
			
		self.teamPtr=0


	##########################TEAM GEN############################
		while self.teamPtr<self.numTeams:
			allyTeam = OptionFactory("ALLYTEAM" + str(self.teamPtr))
			allyTeam.addFromDict({"NumAllies": 0})
			game.addFromOptionInstance(allyTeam)
			
			self.teamPtr+=1;
		self.teamPtr=0

	#########NON-user set SETTINGS ARE OUT OF THE INTERPRETER LOOP
	#########GAME SELECTOR MODULE###############################	
		print("game type is zk")

		game.addFromDict({"Gametype": "Zero-K-master.sdd"})
	
	#########startposi selector MODULE###############################	
		print("start position is   startpostype=2;")###IDK what this module does
		game.addFromDict({"startpostype": 2})
	
	#########autohost ident MODULE###############################	
		game.addFromDict({"hosttype": "SPADS"})
		print("autohost is   hosttype=SPADS;")###IDK what this module does
	
	#########autohost ip MODULE###############################	
		game.addFromDict({"HostIP": ""})
		print("AUTOHOST IP is HostIP=;")###IDK what this module does
	
	#########host port MODULE###############################	
		game.addFromDict({"HostPort": self.battlePort})
		print("HOST port is "+str(self.battlePort))###IDK what this module does		
	
	#########autohost usr MODULE###############################	
		game.addFromDict({
			"AutoHostName": "GGFrog",
			"AutoHostCountryCode": "??",
			"AutoHostRank": 1,
			"AutoHostAccountId": 1024,
			"IsHost": 1,
		})

	#########autohost port MODULE###############################	
		game.addFromDict({"AutohostPort": str(2000+self.battlePort)})
		print("AUTOHOST port is "+str(2000+self.battlePort))###IDK what this module does

	########RESTRICTION GEN########################################	
		print("AUTOHOST NumRestrictions=0;")###IDK what this module does		
		game.addFromDict({"NumRestrictions": 0})

		restrict = OptionFactory("RESTRICT")
		game.addFromOptionInstance(restrict)

	##########MOD OPTIONGEN################################################
		restrict = OptionFactory("MODOPTIONS")
		game.addFromOptionInstance(restrict)

	##########MAP OPTIONGEN################################################
		restrict = OptionFactory("MAPOPTIONS")
		game.addFromOptionInstance(restrict)

		# Write settings
		with open('/tmp/battle' + str(self.battlePort) + '.txt', 'w') as f:
			f.write(game.toString())
		
	#@staticmethod     ##why?
	def engineAlive(self):  #this function seems to be un-needed
		#try:
			#pids = subprocess.check_output(['pidof', 'spring-dedicated'])
		
		try:
			if self.engine.poll() is None:
				return True
		except:
			return False  #the engine has not been running
		return False
		
	def killServer(self):     
		if self.engine:
			self.engine.terminate()
		
		# when engine is alive
		if self.engine.poll() is None:
			return False   #returns false when not terminated(no return code was generated)
		else:
			self.engine = None   #true when terminated with a return code
			return True
				
	def launch(self):
		#os.system('./engine/spring-dedicated /tmp/battle'+str(self.battlePort)+'.txt');
		#self.autohost.free_autohost(self.username)
		#if not self.engineAlive():   #no need to check here, it should be done in hoster
		self.engine = subprocess.Popen(["engine/spring-dedicated", "/tmp/battle" + str(self.battlePort) + '.txt'])
		if self.engine.poll() is None:
			return True    #Successfully launched?
		else:
			self.engine = None
			return False   #not launched?

class OptionFactory:

    def __init__(self, header):
        self.header = '[{0}]'.format(header)
        self.option = ''

    def addFromDict(self, mappingDict):
        for key, value in mappingDict.items():
            if value is None:
                value = ''
            if type(value) is not str:
                value = str(value)

            self.option += str(key) + '=' + str(value) + ';\n'

    def addFromOptionInstance(self, ins):
        self.option = self.option + ins.toString() + '\n'

    def toString(self):
        return self.header + '\n{\n' + self.option + '}'


## Usage
if __name__ == '__main__':
    op = OptionFactory("OPTION")
    print(op.toString())
#    op = OptionFactory("PLAYER0")
#    op.addFromDict({
#        'Name': 'name',
#        'Spector': 0
#        })
#
#    op2 = OptionFactory("PLAYER1")
#    op2.addFromDict({
#        'Name': 'name2',
#        'Spector': 1
#        })
#
#    op.addFromOptionInstance(op2)
#
#    op.addFromDict({
#        'Name': 'name',
#        'Spector': 0
#        })
#
#    print(op.toString())
