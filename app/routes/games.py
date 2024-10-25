from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import timedelta, datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import rest, models, myschemas, database
from ..models import User
from ..rest import get_user
from ..auth import get_current_active_admin
from ..database import engine, get_db
from typing import List
from sqlalchemy.future import select
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user

router = APIRouter()


def check_admin(user: myschemas.User):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admins only."
        )


@router.post("/games/add/", response_model=myschemas.Game)
def create_game(game: myschemas.GameCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    if game.game_name is not None:
        game_name = db.query(models.Game).filter(models.Game.id == game.game_name).first()
        if not game_name:
            raise HTTPException(status_code=404, detail="Game not found")
    else:
        game_name = None

    # Создаем новую Game
    db_game = models.Game(create_date=func.now(), game_name=game_name, game_review=game.game_review)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return db_game


# Получение всех Игр
@router.get("/games/", response_model=List[myschemas.Game])
def read_games(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    games = rest.get_games(db, skip=skip, limit=limit)
    return games


# Получение Игр по ID
@router.get("/games/{game_id}", response_model=myschemas.Game)
def read_fuel(game_id: int, db: Session = Depends(get_db)):
    db_game = rest.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game


@router.delete("/games/delete/", status_code=200)
def delete_games(game_ids: list[int], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    # Проверяем, есть ли Game с данными ID
    stmt = select(models.Game).where(models.Game.id.in_(game_ids))
    result = db.execute(stmt)
    games_to_delete = result.scalars().all()

    if not games_to_delete:
        raise HTTPException(status_code=404, detail="Game(s) not found")

    # Удаляем найденные Game
    for game in games_to_delete:
        db.delete(game)

    db.commit()
    return {"detail": f"Deleted Game(s) with IDs: {game_ids}"}


@router.put("/games/{game_id}", status_code=200)
def update_game(game_id: int, game_data: myschemas.GameUpdate, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    # Найти Game по id
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Обновить данные, если они были переданы
    # обновляем id
    if game_data.id is not None:
        game.id = game_data.id

    # обновляем дату регистрации игры
    if game.service_date is not None:
        game.service_date = game_data.service_date
    else:
        game.service_date = datetime.now()

        # Сохранить изменения в базе данных
    db.commit()
    db.refresh(game)

    return {"detail": "game updated successfully", "game": game}