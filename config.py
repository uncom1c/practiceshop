from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_USER = os.environ.get("POSTGRES_USER")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))



