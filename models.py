from sqlalchemy import Column, INTEGER, VARCHAR, ForeignKey
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Playlist_Clip(Base):
    __tablename__ = 'playlist_clip'

    id = Column(INTEGER, primary_key=True)
    clip_id = Column(INTEGER, ForeignKey('clips.id'))
    play_id = Column(INTEGER, ForeignKey('playlists.id'))

    clip = relation("Clip", backref=backref('playlist_clip', cascade="all, delete-orphan"))
    playlist = relation('PlayList', backref=backref('playlist_clip', cascade="all, delete-orphan"))

    def __init__(self, clip=None, playlist=None):
        self.clip = clip
        self.playlist = playlist

    def __repr__(self):
        return "<Playlist_Clip {}>".format(self.playlist.name + " " + self.clip.title)


class Clip(Base):
    __tablename__ = "clips"

    id = Column(INTEGER, primary_key=True)
    title = Column(VARCHAR(length=128), nullable=False)
    artist = Column(VARCHAR(length=128), nullable=False)
    album = Column(VARCHAR(length=128))

    playlists = relation("PlayList", secondary="playlist_clip")

    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album

    def __repr__(self):
        return "<Clip {}>".format(self.title)


class PlayList(Base):
    __tablename__ = "playlists"

    id = Column(INTEGER, primary_key=True)
    year = Column(INTEGER)
    month = Column(INTEGER)
    name = Column(INTEGER)
    owner_id = Column(INTEGER, ForeignKey('users.id'))
    clips = relation("Clip", secondary="playlist_clip")

    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.name = year + month

    def __repr__(self):
        return "<PlayList {}>".format(str(self.year) + str(self.month) + " of " + str(self.owner_id))


class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(length=32), nullable=False, unique=True)
    passwd = Column(VARCHAR(length=128), nullable=False)

    exchange = relation("Exchange", uselist=False, backref='users')
    playlists = relation("PlayList", order_by="-PlayList.name")

    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd

    def __repr__(self):
        return "<User {}>".format(self.name)


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(INTEGER, primary_key=True)
    owner_id = Column(INTEGER, ForeignKey("users.id"))
    exchange_id = Column(INTEGER)

    def __init__(self, exchange_id):
        self.exchange_id = exchange_id

    def __repr__(self):
        return "<Exchange {}>".format(self.exchange_id)
