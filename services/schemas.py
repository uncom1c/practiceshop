from typing import Annotated
from pydantic import BaseModel, EmailStr
import pydantic

class Item_addDB(BaseModel):
    name: str
    cost: int
    quantity: int
    
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    class Config:
        orm_mode = True
    
class TokenData(BaseModel):
    username: str | None = None

class buy_form(BaseModel):
    name: str
    quantity: Annotated[int, pydantic.Field(gt=0)]

class user_base(BaseModel):
    id: int
    email: EmailStr
    username: str
    money: int
    bought: dict

class buy_order(BaseModel):
    user_id: int
    item_id: int
    quantity: int