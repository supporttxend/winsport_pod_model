from decouple import config
from pydantic import AnyHttpUrl
import json
from typing import List
from decouple import AutoConfig
from pathlib import Path

try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

print(BASE_DIR / "settings.ini")

config = AutoConfig(search_path=BASE_DIR / "settings.ini")


TEMP_ENV = config("ENVIORNMENT")

print("ENVIORNMENT ----------->", config("ENVIORNMENT"))



class BaseConfig:
    """Base config."""
    PROJECT_NAME = config("PROJECT_NAME") + " APIs"


class DevConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    # DB_DRIVER = config("DB_DRIVER")
    # DB_USER = config("DB_USER")
    # DB_PASSWORD = config("DB_PASSWORD")
    # DB_HOST = config("DB_HOST")
    # DB_PORT = config("DB_PORT", cast=int)
    # DATABASE_NAME = config("DATABASE_NAME")
    API_PORT_DOCKER = config("API_PORT_DOCKER", cast=int)
    # ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
    # SECRET_KEY = config("SECRET_KEY")
    MONGO_DB_URI = config("MONGO_DB_URI", cast=str)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = json.loads(config("BACKEND_CORS_ORIGINS"))
    # DEFAULT_SENDER_EMAIL = config("DEFAULT_SENDER_EMAIL")
    # S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    # S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    # S3_CSV_BUCKET = config("S3_CSV_BUCKET")
    # S3_CSV_FOLDER = config("S3_CSV_FOLDER")


class TestConfig(BaseConfig):
    ENV = "testing"
    DEBUG = True


class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    # DB_DRIVER = config("DB_DRIVER")
    # DB_USER = config("DB_USER")
    # DB_PASSWORD = config("DB_PASSWORD")
    # DB_HOST = config("DB_HOST")
    # DB_PORT = config("DB_PORT", cast=int)
    # DATABASE_NAME = config("DATABASE_NAME")
    API_PORT_DOCKER = config("API_PORT_DOCKER", cast=int)
    MONGO_DB_URI = config("MONGO_DB_URI", cast=str)
    # ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
    # SECRET_KEY = config("SECRET_KEY")
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = json.loads(config("BACKEND_CORS_ORIGINS"))
    # DEFAULT_SENDER_EMAIL = config("DEFAULT_SENDER_EMAIL")
    # S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    # S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    # S3_CSV_BUCKET = config("S3_CSV_BUCKET")
    # S3_CSV_FOLDER = config("S3_CSV_FOLDER")


def get_settings():
    if TEMP_ENV == "development":
        settings = DevConfig()
        return settings
    elif TEMP_ENV == "testing":
        settings = TestConfig()
        return settings
    elif TEMP_ENV == "production":
        settings = ProdConfig()
        return settings
    else:
        raise Exception("Invalid  ENV environment variable value")


settings = get_settings()



if __name__ == "__main__":
    settings = get_settings()
