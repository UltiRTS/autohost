#!/usr/bin/env python3
# coding=utf-8
from lib.quirks.dbConnector import past_games
from sqlalchemy.orm import sessionmaker


def recordThisReplay(battleID,dateTime,nameofMap,host,hostIP,playerTeam,playerIP,playerinGameIP,botsTeam,wonTeam,timeElapsed):
	session = sessionmaker(bind=past_games.engine)
	mysql = session()

	pastGame = past_games(bid=battleID,dateT=dateTime,mapName=nameofMap,hostUID=host,host_ip=hostIP ,players=playerTeam,player_ip=playerIP, player_in_game_ip=playerinGameIP,bots=botsTeam,winner=wonTeam,duration=timeElapsed)
	
	mysql.add(pastGame)
	mysql.commit()


if __name__ == "__main__":
	recordThisReplay()
