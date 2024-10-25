from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Float, Table, ARRAY, JSON
from .database import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    regdate = Column(DateTime(timezone=True), default=func.now())
    role = Column(String, default="user")

class Game(Base):
    __tablename__ = "Games"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_name = Column(String, unique=True, index=True)
    game_review = Column(String)
    game_date = Column(DateTime(timezone=True), default=func.now())

class GameComment(Base):
    __tablename__ = "Game_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text_comment = Column(String)
    comment_date = Column(DateTime(timezone=True), default=func.now())
    game = relationship("Game", back_populates= "game_comments")

class GameHack(Base):
    __tablename__ = "Game_hacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name_hack = Column(String)
    hack_date = Column(DateTime(timezone=True), default=func.now())
    game = relationship("Game", back_populates= "game_hacks")

class HackComment(Base):
    __tablename__ = "Hack_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String)
    hack_comment_date = Column(DateTime(timezone=True), default=func.now())
    game_hack = relationship("GameHack", back_populates="hack_comments")