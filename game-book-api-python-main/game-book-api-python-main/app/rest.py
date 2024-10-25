from sqlalchemy.orm import Session
from . import models, myschemas
from datetime import date
from .models import User

# Создание пользователя
def create_user(db: Session, user: myschemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        regdate=date.today(),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Получение пользователя по ID
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Получение всех пользователей
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

# Получение пользователя по имени
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# ----------------------------------------------------------------------------------

# Game
def get_games(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Game).offset(skip).limit(limit).all()
def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()

# GameComment
def get_gamecomments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.GameComment).offset(skip).limit(limit).all()
def get_gamecomment(db: Session, gamecomment_id: int):
    return db.query(models.GameComment).filter(models.GameComment.id == gamecomment_id).first()

# GameHack
def get_gamehacks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.GameHack).offset(skip).limit(limit).all()
def get_gamehack(db: Session, gamehack_id: int):
    return db.query(models.GameHack).filter(models.GameHack.id == gamehack_id).first()

# HackComment
def get_hackcomments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.HackComment).offset(skip).limit(limit).all()
def get_hackcomment(db: Session, hackcomment_id: int):
    return db.query(models.HackComment).filter(models.HackComment.id == hackcomment_id).first()