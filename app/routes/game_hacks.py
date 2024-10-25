from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from .. import rest, models, myschemas, database
from ..models import User
from ..rest import get_user, get_gamehack
from ..auth import get_current_active_admin
from ..database import engine, get_db
from typing import List
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user
import logging

router = APIRouter()


@router.post("/gamehack/add/{id}/", response_model=myschemas.GameHack)
def create_gamehack(gamehack: myschemas.GameHack, game: myschemas.Game.id, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = current_user.id
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_gamehack = models.GameHack(
        text=gamehack.text,
        comment_date=datetime.now(),
        game=game
    )

    # Создаем новую ИХ
    db.add(db_gamehack)
    db.commit()
    db.refresh(db_gamehack)

    return db_gamehack


# Получение gamehack по ID
@router.get("/gamehack/{gamehack_id}", response_model=myschemas.GameHack)
def read_gamehack(gamehack_id: int, db: Session = Depends(get_db)):
    db_gamehack = rest.get_gamehack(db, gamehack_id=gamehack_id)
    if db_gamehack is None:
        raise HTTPException(status_code=404, detail="Game comment not found")
    return db_gamehack


@router.get("/gamehack/", response_model=List[myschemas.GameHack])
def read_gamehack(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    gamehack = rest.get_gamehack(db, skip=skip, limit=limit)
    return gamehack


@router.delete("/gamehacks/{gamehack_id}", status_code=200)
def delete_gamehack(gamehack_id: int, db: Session = Depends(get_db)):
    # Найти комментарий по его id
    gamehack = db.query(models.GameHack).filter(models.GameHack.id == gamehack_id).first()
    if not gamehack:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Удалить gamehack из базы данных
    db.delete(gamehack)
    db.commit()

    return {"detail": f"Deleted game comment with ID: {gamehack_id}"}


@router.put("/gamehack/{gamehack_id}", status_code=200)
def update_gamehack(gamehack_id: int, gamehack_data: myschemas.GameHackUpdate, db: Session = Depends(get_db)):
    # Обновить данные gamehack по id
    gamehack = db.query(models.GameHack).filter(models.GameHack.id == gamehack_id).first()

    if not gamehack:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Обновить данные, если они были переданы
    if gamehack_data.text is not None:
        gamehack.text = gamehack_data.text
        gamehack.comment_date = datetime.now()

    # Сохранить изменения в базе данных
    db.commit()
    db.refresh(gamehack)

    return {"detail": "gamehack updated successfully", "gamehack": gamehack}