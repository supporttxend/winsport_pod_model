from pathlib import Path
import os
from decouple import AutoConfig

BASE_DIR = Path(__file__).resolve().parent.parent

config = AutoConfig(search_path='pod_model/settings.ini')


TEMP_ENV = config("ENVIORNMENT")

print("UMER ----------->", config("ENVIORNMENT"))


class BaseConfig:
    """Base config."""

    PROJECT_NAME = config("PROJECT_NAME") + "_API"


class DevConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET = config("S3_SIG_BUCKET")
    S3_SIG_FOLDER = config("S3_SIG_FOLDER")
    RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
    DATA_SET_FOLDER = config("DATA_SET_FOLDER")


class TestConfig(BaseConfig):
    ENV = "testing"
    DEBUG = True


class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = False

    S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET = config("S3_SIG_BUCKET")
    S3_SIG_FOLDER = config("S3_SIG_FOLDER")
    RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
    DATA_SET_FOLDER = config("DATA_SET_FOLDER")


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
