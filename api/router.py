from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from psycopg2 import IntegrityError
from db.schemas import (
    UserCreate,
    Token,
    buy_form,
    buy_order,
    user_base,
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, item_table, order_table
from config import JWT_ALGORITHM, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
# from sqlalchemy.exc import *

from services.user_service import (
    verify_password,
    get_password_hash,
    encode_user,
    get_email,
    get_item,
    get_username,
    get_id,
    create_item,
    create_access_token,
    get_current_user,
    buy_service
)
router = APIRouter()


@router.get("/me", response_model=None)
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
    try:
        order_create = await buy_service(
            item, user, db
        )
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )
    return order_create


