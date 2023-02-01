import os
from pathlib import Path

from decouple import AutoConfig

# import os, sys
# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

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

    PROJECT_NAME = config("PROJECT_NAME") + "_API"


class DevConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    DOCKER = config("DOCKER", cast=bool)
    S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET = config("S3_SIG_BUCKET")
    S3_SIG_FOLDER = config("S3_SIG_FOLDER")
    RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
    DATA_SET_FOLDER = BASE_DIR.parent / "input" / config("DATA_SET_FOLDER")
    SM_MODEL_DIR = BASE_DIR.parent / "model"
    SM_CHECK_POINT_DIR = BASE_DIR.parent / "checkpoints"

    # tensorflow pipline variables
    # PIPE_LINE_SESSION = LocalPipelineSession()


class TestConfig(BaseConfig):
    ENV = "testing"
    DEBUG = True
    DOCKER = config("DOCKER", cast=bool)
    S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET = config("S3_SIG_BUCKET")
    S3_SIG_FOLDER = config("S3_SIG_FOLDER")
    RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
    DATA_SET_FOLDER = config("DATA_SET_FOLDER")
    PRE_PROCESSING_IN = BASE_DIR.parent / "data"
    PRE_PROCESSING_OUT = BASE_DIR.parent.parent / "output"
    SM_MODEL_DIR = BASE_DIR.parent / "model"
    SM_CHECK_POINT_DIR = BASE_DIR.parent / "checkpoints"

    # tensorflow pipline variables
    # PIPE_LINE_SESSION = LocalPipelineSession()


class ProdConfig(BaseConfig):
    ENV = "production"
    DEBUG = True
    DOCKER = config("DOCKER", cast=bool)
    S3_ACCESS_KEY_ID = config("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")
    S3_SIG_BUCKET = config("S3_SIG_BUCKET")
    S3_SIG_FOLDER = config("S3_SIG_FOLDER")
    RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
    DATA_SET_FOLDER = config("DATA_SET_FOLDER")
    PRE_PROCESSING_IN = BASE_DIR.parent / "data"
    PRE_PROCESSING_OUT = BASE_DIR.parent.parent / "output"
    SM_MODEL_DIR = BASE_DIR.parent / "model"
    SM_CHECK_POINT_DIR = BASE_DIR.parent / "checkpoints"

    # tensorflow pipline variables
    # PIPE_LINE_SESSION = PipelineSession()


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
