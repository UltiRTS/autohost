
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime

Base = declarative_base()
class past_games(Base):
	__tablename__ = 'past_games'

	bid = Column('bid',Integer, primary_key=True)
	dateT = Column('date_time',DateTime, nullable=False)
	mapName = Column('map',String(64), nullable=False)
	hostUID = Column('host',Integer, nullable=False)
	host_ip = Column('host_ip',String(64), nullable=False)
	players = Column('players',String(64), nullable=False)
	player_ip = Column('player_ip',String(64), nullable=False)
	player_in_game_ip = Column('player_in_game_ip',String(64), nullable=False)
	winner = Column('winner',String(64), nullable=False)
	duration = Column('duration',String(64), nullable=False)

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.username)

class users(Base):
	__tablename__ = 'users'

	uId = Column('id',Integer, primary_key=True)
	username = Column('username',String(64), nullable=True)
	password = Column('password',String(64), nullable=True)
	register_date = Column('register_date',DateTime, nullable=True)
	last_login = Column('last_login',DateTime, nullable=True)
	last_ip = Column('last_ip',String(64), nullable=True)
	ingame_time = Column('ingame_time',Integer, nullable=True)
	access = Column('access',String(64), nullable=True)
	email = Column('email',String(64), nullable=True)

	def __repr__(self):
		return '%s(%r)' % (self.__class__.__name__, self.username)


