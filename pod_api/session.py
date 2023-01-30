from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL as sqlalchemy_engine_URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

engine = create_engine(
    sqlalchemy_engine_URL.create(
        drivername=settings.DB_DRIVER,  # e.g "mysql" or "pymsql+mysql"
        username=settings.DB_USER,  # e.g. "my-database-user"
        password=settings.DB_PASSWORD,  # e.g. "my-database-password"
        host=settings.DB_HOST,  # e.g. "127.0.0.1"
        port=settings.DB_PORT,  # e.g. 3306
        database=settings.DATABASE_NAME,  # e.g. "my-database-name"
    ),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
