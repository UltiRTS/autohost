from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime

Base = declarative_base()
class past_games(Base):

	engine = create_engine('mysql://lobbyServer:lobbyServer@localhost/lobbyServer')

	__tablename__ = 'past_games'

	bid = Column('bid',Integer, primary_key=True)
	dateT = Column('date_time',DateTime, nullable=False)
	mapName = Column('map',String(64), nullable=False)
	hostUID = Column('host',Integer, nullable=False)
	host_ip = Column('host_ip',String(64), nullable=False)
	players = Column('players',String(64), nullable=False)
	player_ip = Column('player_ip',String(64), nullable=False)
	player_in_game_ip = Column('player_in_game_ip',String(64), nullable=False)
	bots = Column('bots',String(64), nullable=False)
	winner = Column('winner',String(64), nullable=False)
	duration = Column('duration',String(64), nullable=False)


	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.username)
