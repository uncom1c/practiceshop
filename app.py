from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
# from auth.auth import auth_backend
import uvicorn
from db.base import metadata
from db.database import engine
# from auth.database import User
# from auth.manager import get_user_manager

# from auth.schemas import UserCreate, UserRead

import os


from api.router import router as api_router
from api.auth.router import router as auth_router
from api.search.router import router as search_router
from api.shop.router import router as shop_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    #
    await create_tables()
    
    yield

    # await drop_tables()

    # 


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def drop_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


app = FastAPI(lifespan=lifespan)



app.include_router(router=api_router)
app.include_router(router=auth_router,  prefix="/auth" , tags=["auth"])
app.include_router(router=search_router,prefix="/search" , tags=["search"])
app.include_router(router=shop_router,  prefix="/shop" ,  tags=["shop"])