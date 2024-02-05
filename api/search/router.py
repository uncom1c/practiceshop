from fastapi import APIRouter, Depends, HTTPException, status
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, item_table, order_table
# from sqlalchemy.exc import *

from services.user_service import (
    service_getuser_by_jwt,
    get_email,
    get_username
)
router = APIRouter()

@router.get("/user")
async def user_login_handler(jwt_token, db: AsyncSession = Depends(get_async_session)):
    try:
        user = await service_getuser_by_jwt(jwt_token, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )

    return user

@router.get("/email")
async def search_email_handler(email, db: AsyncSession = Depends(get_async_session)):
    # decode and verify jwt
    # get user from db by jwt
    # return user

    return await get_email(email, db)

@router.get("/username")
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

@router.get("/allitems")
async def allitems_handler(db: AsyncSession = Depends(get_async_session)):
    query = item_table.select()
    result = await db.execute(query)

    return result.mappings().all()