#!/usr/bin/env python3
# coding=utf-8
from sqlalchemy import create_engine
from lib.quirks.dbPrototype import users
from lib.quirks.dbPrototype import past_games
from sqlalchemy.orm import sessionmaker
engine = create_engine('mysql://lobbyServer:lobbyServer@localhost/lobbyServer',encoding='utf-8')

def recordThisReplay (battleID,dateTime,nameofMap,host,hostIP,playerTeam,playerIP, playerinGameIP,wonTeam,timeElapsed):
	
	Session = sessionmaker(bind=engine)
	session = Session()

	pastGame = past_games(bid=battleID,dateT=dateTime,mapName=nameofMap,hostUID=host,host_ip=hostIP ,players=playerTeam,player_ip=playerIP, player_in_game_ip=playerinGameIP,winner=wonTeam,duration=timeElapsed)
	print('writing to db:'+str(past_games))
	session.add(pastGame)
	session.commit()

def getUserId(inputArg):
	Session = sessionmaker(bind=engine)
	session= Session()
	#session.query(users).filter_by(username='Teresa').uId 
	#session.query(users).filter_by(username=aa).uId()
	#print(session.query(users).filter_by(username=aa)).one().uId
	print(session.query(users).filter_by(username=inputArg).one().uId)
	return session.query(users).filter_by(username=inputArg).one().uId
	
def getUserIP(inputArg):
	Session = sessionmaker(bind=engine)
	session= Session()
	#session.query(users).filter_by(username='Teresa').uId 
	#session.query(users).filter_by(username=aa).uId()
	#print(session.query(users).filter_by(username=aa)).one().uId
	print(session.query(users).filter_by(username=inputArg).one().last_ip)
	return session.query(users).filter_by(username=inputArg).one().last_ip

if __name__ == "__main__":
	recordThisReplay()
