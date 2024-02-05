from datetime import timedelta, timezone, datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
from db.schemas import (
    Item_addDB,
    UserCreate,
    TokenData,
    buy_form,
    user_base,
    buy_order
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, item_table, order_table
from config import JWT_ALGORITHM, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from sqlalchemy.exc import *
import random

# from api.dependencies import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def encode_user(user: UserCreate):
    return UserCreate(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )


async def get_username(username, db: AsyncSession):
    query = user_table.select().where(user_table.c.username == username)
    found_user = await db.execute(query)

    found_user = found_user.mappings().first()
    if found_user:
        return found_user
    else:
        return None


async def get_item(itemname, db: AsyncSession):
    query = item_table.select().where(item_table.c.name == itemname)
    found_item = await db.execute(query)

    found_item = found_item.mappings().first()
    if found_item:
        return found_item
    else:
        return None


async def get_email(email, db: AsyncSession):
    query1 = user_table.select().where(user_table.c.email == email)
    found_user = await db.execute(query1)
    found_user = found_user.mappings().one()

    if found_user:
        return found_user
    else:
        return None


async def get_id(_id, db: AsyncSession):
    query1 = user_table.select().where(user_table.c.id == _id)
    found_user = await db.execute(query1)
    found_user = found_user.mappings().one()
    if found_user:
        return found_user
    else:
        return None


async def create_item(item_name):
    item_cost = random.randint(1, 100)
    item_quantity = random.randint(0, 10)
    return Item_addDB(name=item_name, cost=item_cost, quantity=item_quantity)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_async_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_username(token_data.username, db)
    if user is None:
        raise credentials_exception
    return user



async def buy_service(
    item: buy_form,
    user: user_base,
    db: AsyncSession
):
    itemindb = await get_item(item.name, db)
    
    if not itemindb:
        raise BaseException("Такого нету иди нахуй")
    
    if itemindb.quantity < item.quantity:
        raise BaseException("Еблан наличия нет")
    
    finalcost = itemindb.cost * item.quantity

    if user.money < finalcost:
        raise BaseException("Безденежное чмо")
    
    order_create = buy_order(item_id = itemindb.id, quantity=item.quantity, user_id = user.id )

    query = user_table.update().where(user_table.c.id == user.id).values(money = user.money - finalcost)
    query1 = item_table.update().where(item_table.c.id == itemindb.id).values(quantity = itemindb.quantity - item.quantity)
    query2 = order_table.insert().values(**order_create.dict())
    await db.execute(query)
    await db.execute(query1)
    await db.execute(query2)
    await db.commit()
    return order_create