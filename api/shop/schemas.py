from typing import Annotated
from pydantic import BaseModel, EmailStr
import pydantic

class buy_form(BaseModel):
    name: str
    quantity: Annotated[int, pydantic.Field(gt=0)]

class user_base(BaseModel):
    id: int
    email: EmailStr
    username: str
    money: int
    bought: dict

    