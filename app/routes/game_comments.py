from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from .. import rest, models, myschemas, database
from ..models import User
from ..rest import get_user, get_gamecomment
from ..auth import get_current_active_admin
from ..database import engine, get_db
from typing import List
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user
import logging

router = APIRouter()


@router.post("/gamecomment/add/{id}/", response_model=myschemas.GameComment)
def create_gamecomment(gamecomment: myschemas.GameCommentCreate, game: myschemas.Game.id, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = current_user.id
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_gamecomment = models.GameComment(
        text=gamecomment.text,
        comment_date=datetime.now(),
        game=game
    )

    # Создаем новый комментарий
    db.add(db_gamecomment)
    db.commit()
    db.refresh(db_gamecomment)

    return db_gamecomment


# Получение gamecomment по ID
@router.get("/gamecomment/{gamecomment_id}", response_model=myschemas.GameComment)
def read_gamecomment(gamecomment_id: int, db: Session = Depends(get_db)):
    db_gamecomment = rest.get_gamecomment(db, gamecomment_id=gamecomment_id)
    if db_gamecomment is None:
        raise HTTPException(status_code=404, detail="Game comment not found")
    return db_gamecomment


@router.get("/gamecomment/", response_model=List[myschemas.GameComment])
def read_gamecomment(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    gamecomment = rest.get_gamecomment(db, skip=skip, limit=limit)
    return gamecomment


@router.delete("/gamecomments/{gamecomment_id}", status_code=200)
def delete_gamecomment(gamecomment_id: int, db: Session = Depends(get_db)):
    # Найти комментарий по его id
    gamecomment = db.query(models.GameComment).filter(models.GameComment.id == gamecomment_id).first()
    if not gamecomment:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Удалить комментарий из базы данных
    db.delete(gamecomment)
    db.commit()

    return {"detail": f"Deleted game comment with ID: {gamecomment_id}"}


@router.put("/gamecomment/{gamecomment_id}", status_code=200)
def update_gamecomment(gamecomment_id: int, gamecomment_data: myschemas.GameCommentUpdate, db: Session = Depends(get_db)):
    # Обновить данные game comment по id
    gamecomment = db.query(models.GameComment).filter(models.GameComment.id == gamecomment_id).first()

    if not gamecomment:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Обновить данные, если они были переданы
    if gamecomment_data.text is not None:
        gamecomment.text = gamecomment_data.text
        gamecomment.comment_date = datetime.now()

    # Сохранить изменения в базе данных
    db.commit()
    db.refresh(gamecomment)

    return {"detail": "gamecomment updated successfully", "gamecomment": gamecomment}