from sqlalchemy.orm import Session
from datetime import datetime
import random
from ..database import SessionLocal
from ..models import User, Game, GameComment, GameHack, HackComment
from ..auth import get_password_hash

# Подключаемся к базе данных
db: Session = SessionLocal()


# Функция для добавления Пользователей
def add_users(db: Session):
    users_data = [
        {"username": "admin1", "email": "admin1@example.com", "password": f"{get_password_hash('hashed_password')}",
         "role": "admin"},
        {"username": "admin2", "email": "admin2@example.com", "password": f"{get_password_hash('hashed_password')}",
         "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "password": f"{get_password_hash('hashed_password')}",
         "role": "user"},
        {"username": "user2", "email": "user2@example.com", "password": f"{get_password_hash('hashed_password')}",
         "role": "user"},
        {"username": "user3", "email": "user3@example.com", "password": f"{get_password_hash('hashed_password')}",
         "role": "user"},
    ]
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    db.commit()


# Функция для добавления Игр
def add_games(db: Session):
    for i in range(5):
        game = Game(adress=f"Test Address {i + 1}")
        db.add(game)
    db.commit()


# Функция для добавления Игровых комментариев и привязки их к Играм
def add_game_comments(db: Session):
    games = db.query(Game).all()
    game_comment_count = 20
    game_comments = []

    for i in range(game_comment_count):
        game = random.choice(games)
        game_comment = GameComment(game_id=game.id, comment_date=datetime.now())
        db.add(game_comment)
        game_comments.append(game_comment)
    db.commit()
    return game_comments

# Функция для добавления ИХ и привязки их к Играм
def add_game_hacks(db: Session):
    games = db.query(Game).all()
    game_hack_count = 20
    game_hacks = []

    for i in range(game_hack_count):
        game = random.choice(games)
        game_hack = GameHack(game_id=game.id, comment_date=datetime.now())
        db.add(game_hack)
        game_hacks.append(game_hack)
    db.commit()
    return game_hacks

# Функция для добавления комментариев ИХ и привязки их к ИХ
def add_game_hack_comments(db: Session):
    game_hacks = db.query(GameHack).all()
    hack_comment_count = 40
    hack_comments = []

    for i in range(hack_comment_count):
        game_hack = random.choice(game_hacks)
        hack_comment = HackComment(game_hack_id=game_hack.id, comment_date=datetime.now())
        db.add(hack_comment)
        hack_comments.append(hack_comment)
    db.commit()
    return hack_comments

# Основная функция, добавляющая все данные
def populate_db():
    print("Добавляем Пользователей...")
    add_users(db)
    print("Добавляем Игры...")
    add_games(db)
    print("Добавляем Игровые комментарии и привязываем их к Играм...")
    add_game_comments(db)
    print("Добавляем ИХ и привязываем их к Играм...")
    add_game_hacks(db)
    print("Добавляем комментарии к ИХ и привязываем их к ИХ...")
    add_game_hack_comments(db)
    print("Загрузка тестовых данных завершена!")

# Запуск функции заполнения
populate_db()
db.close()