import json
from pathlib import Path
from typing import List

from decouple import AutoConfig, config
from pydantic import AnyHttpUrl

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
    API_PORT_DOCKER = config("API_PORT_DOCKER", cast=int)
    MONGO_DB_URI = config("MONGO_DB_URI", cast=str)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = json.loads(config("BACKEND_CORS_ORIGINS"))
    S3_BUCKET_NODE=config("S3_BUCKET_NODE")


class TestConfig(BaseConfig):
    ENV = "testing"
    DEBUG = True


class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    API_PORT_DOCKER = config("API_PORT_DOCKER", cast=int)
    MONGO_DB_URI = config("MONGO_DB_URI", cast=str)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = json.loads(config("BACKEND_CORS_ORIGINS"))
    S3_BUCKET_NODE=config("S3_BUCKET_NODE")


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
