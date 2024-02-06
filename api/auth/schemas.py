
from pydantic import BaseModel, EmailStr

class user_base(BaseModel):
    id: int
    email: EmailStr
    username: str
    money: int
    bought: dict


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
