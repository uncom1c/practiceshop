from typing import Annotated, Optional
import uuid

from pydantic import BaseModel, EmailStr
import pydantic
import pydantic_core

# class user_base(BaseModel):
#     id: int
#     email: EmailStr
#     username: str
#     money: int
#     bought: dict

# class UserRead(user_base):
#     password: str
    
#     class Config:
#         orm_mode = True


# class UserCreate(BaseModel):
#     email: EmailStr
#     username: str
#     password: str
#     class Config:
#         orm_mode = True

# class UserforUser(user_base):

#     class Config:
#         orm_mode = True

# class User_login(BaseModel):
#     email: EmailStr
#     password: str

# class Item_addDB(BaseModel):
#     name: str
#     cost: int
#     quantity: int
    
# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class TokenData(BaseModel):
#     username: str | None = None

# class buy_form(BaseModel):
#     name: str
#     quantity: Annotated[int, pydantic.Field(gt=0)]

# class buy_order(BaseModel):
#     user_id: int
#     item_id: int
#     quantity: int