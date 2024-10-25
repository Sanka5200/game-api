from fastapi import FastAPI, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session
from . import rest, models, myschemas, database
from .myschemas import LoginRequest
from .models import User
from .rest import get_user
from .auth import get_current_active_admin
from .database import engine, get_db
from typing import List
from .auth import create_access_token, verify_password, get_password_hash, get_current_user
import logging, os
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError


from .routes import games, game_comments, game_hacks, hack_comments

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Создание всех таблиц в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Создание нового пользователя
@app.post("/create-user/", response_model=myschemas.User)
def create_user(user: myschemas.UserCreate, db: Session = Depends(database.get_db)):
    # Проверка длины пароля
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль не должен быть короче 8-ми символов"
        )
    
    # Проверка уникальности email
    db_email_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такая почта уже зарегистрирована"
        )

    # Проверка уникальности username
    db_username_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже зарегистрирован"
        )

    # Хеширование пароля
    hashed_password = get_password_hash(user.password)

    # Создание нового пользователя
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role if user.role else "user",
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Произошла ошибка при сохранении пользователя, возможно, из-за неуникальных данных"
        )
    
    return db_user

from sqlalchemy.orm import Session
from .models import User
from .auth import get_password_hash
from .database import get_db

# -----------------------------------------------------------------------------------------------------
# Функция для хэширования всех паролей, так как на этапе до внедрения токенов я пароли не хэшировал, то после внедрения токенов пришлось дописывать код, который бы хэшировал пароли, которые я не хэшировал (проще было бы бд снести и по новой создавать пользователей)
def hash_passwords(db: Session):
    users = db.query(User).all()  # Получаем всех пользователей
    for user in users:
        if not user.password.startswith("$2b$"):  # Проверяем, что пароль не хэширован (bcrypt хэши обычно начинаются с "$2b$")
            user.password = get_password_hash(user.password)  # Хэшируем пароль
    db.commit()  # Сохраняем изменения в базе данных
    print("Пароли успешно хэшированы")

# Функция для запуска скрипта
def run_hashing():
    with next(get_db()) as db:  # Открываем сессию базы данных
        hash_passwords(db)  # Запускаем хэширование паролей
# run_hashing()
# -----------------------------------------------------------------------------------------------------

# Аутентификация пользователя
def authenticate_user(db: Session, username: str, password: str):
    user = rest.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return False
    return user

# Проверка роли пользователя
def check_admin(user: myschemas.User):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admins only."
        )

# Эндпоинт для получения токена
@app.post("/token")
async def login_for_access_token(login_request: LoginRequest, db: Session = Depends(database.get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=1200)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/")
async def read_admin_data(current_user: User = Depends(get_current_active_admin)):
    return {"message": f"Приветствую, {current_user.username}, ты зашёл в систему как admin."}

# Получение всех пользователей
@app.get("/admin/users/", response_model=List[myschemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    users = rest.get_users(db, skip=skip, limit=limit)
    logger.warning(f"Crap...:")
    return users

# Получение пользователя по ID
@app.get("/admin/users/{user_id}/", response_model=myschemas.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    db_user = rest.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user

@app.get("/users/me/", response_model=myschemas.User)
def read_user_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me/update/", response_model=myschemas.User)
async def update_current_user(
    user_update: myschemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверка и обновление имени пользователя
    if user_update.username is not None:
        user_with_same_username = db.query(models.User).filter(models.User.username == user_update.username).first()
        if user_with_same_username and user_with_same_username.id != current_user.id:
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
        current_user.username = user_update.username

    # Проверка и обновление email
    if user_update.email is not None:
        user_with_same_email = db.query(models.User).filter(models.User.email == user_update.email).first()
        if user_with_same_email and user_with_same_email.id != current_user.id:
            raise HTTPException(status_code=400, detail="Электронная почта уже зарегистрирована")
        current_user.email = user_update.email

    # Обновление пароля (хешируем новый пароль)
    if user_update.password is not None:
        if verify_password(user_update.old_password, current_user.password):
            current_user.password = get_password_hash(user_update.password)
        else:
            raise HTTPException(status_code=400, detail="Ваш старый пароль неверный. Установите новый пароль")

    # Сохраняем изменения
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/admin/users/{user_id}/", status_code=200)
def delete_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_admin(current_user)
    # Найти пользователя по его id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удалить пользователя из базы данных
    db.delete(user)
    db.commit()
    return {"detail": f"Удален пользователь с идентификатором: {user_id}"}


# штучка, которая позволяет подключить эндпоинты из другого файла
app.include_router(games.router)
app.include_router(game_hacks.router)
app.include_router(hack_comments.router)
app.include_router(game_comments.router)