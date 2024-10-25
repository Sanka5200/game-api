from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from .. import rest, models, myschemas, database
from ..models import User
from ..rest import get_user, get_hackcomment
from ..auth import get_current_active_admin
from ..database import engine, get_db
from typing import List
from ..auth import create_access_token, verify_password, get_password_hash, get_current_user
import logging

router = APIRouter()


@router.post("/hackcomment/add/{id}/", response_model=myschemas.HackComment)
def create_hackcomment(hackcomment: myschemas.hackcomment, game_hack: myschemas.HackComment.id, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = current_user.id
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_hackcomment = models.HackComment(
        text=hackcomment.text,
        hackcomment_date=datetime.now(),
        game_hack=game_hack
    )

    # Создаем новый hackcomment
    db.add(db_hackcomment)
    db.commit()
    db.refresh(db_hackcomment)

    return db_hackcomment


# Получение hackcomment по ID
@router.get("/hackcomment/{hackcomment_id}", response_model=myschemas.HackComment)
def read_hackcomment(hackcomment_id: int, db: Session = Depends(get_db)):
    db_hackcomment = rest.get_hackcomment(db, hackcomment_id=hackcomment_id)
    if db_hackcomment is None:
        raise HTTPException(status_code=404, detail="Game comment not found")
    return db_hackcomment


@router.get("/hackcomment/", response_model=List[myschemas.HackComment])
def read_hackcomment(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    hackcomment = rest.get_hackcomment(db, skip=skip, limit=limit)
    return hackcomment


@router.delete("/hackcomments/{hackcomment_id}", status_code=200)
def delete_hackcomment(hackcomment_id: int, db: Session = Depends(get_db)):
    # Найти hackcomment по его id
    hackcomment = db.query(models.HackComment).filter(models.HackComment.id == hackcomment_id).first()
    if not hackcomment:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Удалить hackcomment из базы данных
    db.delete(hackcomment)
    db.commit()

    return {"detail": f"Deleted game comment with ID: {hackcomment_id}"}


@router.put("/hackcomment/{hackcomment_id}", status_code=200)
def update_hackcomment(hackcomment_id: int, hackcomment_data: myschemas.HackCommentUpdate, db: Session = Depends(get_db)):
    # Обновить данные hackcomment по id
    hackcomment = db.query(models.HackComment).filter(models.HackComment.id == hackcomment_id).first()

    if not hackcomment:
        raise HTTPException(status_code=404, detail="Game comment not found")

    # Обновить данные, если они были переданы
    if hackcomment_data.text is not None:
        hackcomment.text = hackcomment_data.text
        hackcomment.comment_date = datetime.now()

    # Сохранить изменения в базе данных
    db.commit()
    db.refresh(hackcomment)

    return {"detail": "hackcomment updated successfully", "hackcomment": hackcomment}