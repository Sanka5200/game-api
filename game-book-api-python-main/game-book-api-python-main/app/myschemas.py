from pydantic import BaseModel, EmailStr, constr, Json
from typing import Optional, List
from datetime import date, datetime

class UserBase(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    role: Optional[str] = "user"

class UserCreate(UserBase):
    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, max_length=50)] = None   # type: ignore
    password: Optional[constr(min_length=8)] = None # type: ignore

class User(UserBase):
    id: Optional[int] = None
    username: str
    regdate: Optional[datetime]=None

    class Config:
        orm_mode = True
        from_attributes = True

class UserUpdate(UserBase):
    username: Optional[constr(min_length=3, max_length=50)] = None   # type: ignore
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None # type: ignore
    old_password: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# ----------------------------------------------------------------
class GameBase(BaseModel):
    id: Optional[int] = None
    game_date: Optional[datetime] = None

class GameCreate(GameBase):
    id: Optional[int] = None
    game_name: Optional["GameBase"] = None
    game_review: Optional["GameBase"] = None
    game_date: Optional[datetime] = datetime.now()

class Game(GameBase):
    id: int
    game_name: str
    game_review: Optional["GameBase"] = None
    service_date: Optional[datetime] = datetime.now()

    class Config:
        orm_mode = True
        from_attributes = True

class GameUpdate(Game):
    game_name: Optional[str] = None
    game_review: Optional[str] = None
    service_date: Optional[datetime] = datetime.now()
# ----------------------------------------------------------------
class GameCommentBase(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    comment_date = Optional[datetime] = None
    game: Optional[int] = None

class GameCommentCreate(GameCommentBase):
    id: int
    text: str
    comment_date = Optional[datetime] = datetime.now()
    game: int

class GameComment(GameCommentBase):
    id: int
    text: str
    comment_date: Optional[datetime] = datetime.now()
    game: int

    class Config:
        orm_mode = True
        from_attributes = True

class GameCommentUpdate(GameComment):
    text: Optional[str] = None
    comment_date: Optional[datetime] = datetime.now()
# ----------------------------------------------------------------

class GameHackBase(BaseModel):
    id: Optional[int] = None
    name_hack: Optional[str] = None
    hack_date: Optional[datetime] = None
    game: Optional[int] = None

class GameHackCreate(GameHackBase):
    id: int
    name_hack: str
    hack_date: Optional[datetime] = datetime.now()
    game: int

class GameHack(GameHackBase):
    id: int
    name_hack: str
    hack_date: Optional[datetime] = datetime.now()
    game: int

    class Config:
        orm_mode = True
        from_attributes = True

class GameHackUpdate(GameHack):
    name_hack: str
    hack_date: Optional[datetime] = datetime.now()

# ----------------------------------------------------------------

class HackCommentBase(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    hack_comment_date: Optional[datetime] = None
    game_hack: Optional[int] = None

class HackCommentCreate(HackCommentBase):
    text_hack_comment: str

class HackComment(HackCommentBase):
    id: int
    text: str
    hack_comment_date: Optional[datetime] = datetime.now()
    game_hack: int

    class Config:
        orm_mode = True
        from_attributes = True

class HackCommentUpdate(HackCommentBase):
    text: str
    hack_comment_date: Optional[datetime] = datetime.now()