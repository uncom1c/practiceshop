from datetime import timedelta, timezone, datetime
import time
from typing import Annotated, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from sqlalchemy import Column
from db.schemas import (
    Item_addDB,
    User_login,
    UserCreate,
    UserforUser,
    Token,
    TokenData,
    UserRead,
    buy_form,
    buy_order,
    user_base,
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, item_table, order_table
from config import JWT_ALGORITHM, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from sqlalchemy.exc import *
from sqlalchemy.orm import defer
import random

# from api.dependencies import *
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


router = APIRouter()


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


async def get_username(username, db: AsyncSession = Depends(get_async_session)):
    query = user_table.select().where(user_table.c.username == username)
    found_user = await db.execute(query)

    found_user = found_user.mappings().first()
    if found_user:
        return found_user
    else:
        return None


async def get_item(itemname, db: AsyncSession = Depends(get_async_session)):
    query = item_table.select().where(item_table.c.name == itemname)
    found_item = await db.execute(query)

    found_item = found_item.mappings().first()
    if found_item:
        return found_item
    else:
        return None


async def get_email(email, db: AsyncSession = Depends(get_async_session)):
    query1 = user_table.select().where(user_table.c.email == email)
    found_user = await db.execute(query1)
    found_user = found_user.mappings().one()

    if found_user:
        return found_user
    else:
        return None


async def get_id(_id, db: AsyncSession = Depends(get_async_session)):
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


@router.get("/me")
async def me_handler(user: Annotated[user_base, Depends(get_current_user)]):
    return user


@router.post("/register")
async def register_handler(
    user_create: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    # validate
    # put to db
    # return from db
    # inserted_user = user.insert().values(email = user_create.email, username = user_create.username, password = user_create.password)
    # if await get_email(user_create.email, db):
    #     return "email taken"
    # if await get_username(user_create.username, db):
    #     return "username taken"

    user_create = encode_user(user_create)
    query = user_table.insert().values(**user_create.dict())

    try:
        inserted_user = await db.execute(query)
    except IntegrityError:
        return "такой пользователь уже есть, ХУЕСОС"

    await db.commit()

    return (
        f"Поздравляем, вы зарегались, пользователь {inserted_user.inserted_primary_key}"
    )


# @router.post("/login")
# async def login_handler(user_login: User_login, db: AsyncSession = Depends(get_async_session)):

#     result = await get_email(user_login.email, db)

#     if not result:
#         return "no such user"

#     if not verify_password(user_login.password, result["password"]):
#         return "wrong password"

#     # generate jwt
#     # return jwt
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     jwt_token =  create_access_token(data={"sub": result["username"]}, expires_delta=access_token_expires)

#     return Token(access_token = jwt_token, token_type="bearer")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    result = await get_username(form_data.username, db)

    if not result:
        return "no such user"

    if not verify_password(form_data.password, result["password"]):
        return "wrong password"

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": result["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/user")
async def user_login_handler(jwt_token, db: AsyncSession = Depends(get_async_session)):
    # decode and verify jwt
    # get user from db by jwt
    # return user

    try:
        decoded_jwt = jwt.decode(
            jwt_token,
            JWT_SECRET,
            JWT_ALGORITHM,
        )
        user_id = decoded_jwt["id"]
    except jwt.exceptions.DecodeError:
        return "ПАШЁЛ НАХУЙ ХАКЕР Я ТВАЮ МАМАШУ ЕБАЛ"
    except jwt.exceptions.ExpiredSignatureError:
        return "перелогинься, время вышло"
    except:
        return "Ошибка какая-то, бля хз"

    result = await get_id(user_id, db)
    return result


@router.get("/search/email")
async def search_email_handler(email, db: AsyncSession = Depends(get_async_session)):
    # decode and verify jwt
    # get user from db by jwt
    # return user

    return await get_email(email, db)


@router.get("/search/username")
async def search_user_name_handler(
    username, db: AsyncSession = Depends(get_async_session)
):
    # decode and verify jwt
    # get user from db by jwt
    # return user

    return await get_username(username, db)


@router.get("/allusers")
async def allusers_handler(db: AsyncSession = Depends(get_async_session)):
    query = user_table.select()
    result = await db.execute(query)

    return result.mappings().all()

@router.get("/allorders")
async def allorders_handler(db: AsyncSession = Depends(get_async_session)):
    query = order_table.select()
    result = await db.execute(query)

    return result.mappings().all()


@router.get("/zalupa")
async def zalupa_handler():
    return "hello world"


@router.post("/add_item")
async def add_item(item_name, db: AsyncSession = Depends(get_async_session)):
    new_item = await create_item(item_name)
    query = item_table.insert().values(**new_item.dict())

    try:
        inserted_item = await db.execute(query)
    except IntegrityError:
        return "такой предмет уже есть, ХУЕСОС"

    await db.commit()

    return f"Поздравляем, вы пополнили магазин, добавили {item_name} под id {inserted_item.inserted_primary_key}"


@router.get("/allitems")
async def allitems_handler(db: AsyncSession = Depends(get_async_session)):
    query = item_table.select()
    result = await db.execute(query)

    return result.mappings().all()


@router.post("/buy")
async def buy_handler(
    item: buy_form,
    user: Annotated[user_base, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_session),
):
    itemindb = await get_item(item.name, db)
    
    if not itemindb:
        return "Такого нету иди нахуй"
    
    if itemindb.quantity < item.quantity:
        return "Еблан наличия нет"
    
    finalcost = itemindb.cost * item.quantity

    if user.money < finalcost:
        return "Безденежное чмо"
    
    order_create = buy_order(item_id = itemindb.id, quantity=item.quantity, user_id = user.id )

    query = user_table.update().where(user_table.c.id == user.id).values(money = user.money - finalcost)
    query1 = item_table.update().where(item_table.c.id == itemindb.id).values(quantity = itemindb.quantity - item.quantity)
    query2 = order_table.insert().values(**order_create.dict())
    await db.execute(query)
    await db.execute(query1)
    await db.execute(query2)
    await db.commit()

    return order_create


