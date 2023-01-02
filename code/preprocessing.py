from config import settings
from cloudpathlib import CloudPath
from pathlib import Path
import os
import shutil
import splitfolders
import time
import os
import numpy as np
import shutil
import random
import glob

try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

S3_SIG_FOLDER = settings.S3_SIG_FOLDER
S3_SIG_BUCKET = settings.S3_SIG_BUCKET
RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
PRE_PROCESSING_IN = settings.PRE_PROCESSING_IN
PRE_PROCESSING_OUT = settings.PRE_PROCESSING_OUT


# def download_dataset(start, end):
#     try:
#         if os.path.exists(PRE_PROCESSING_IN):
#             shutil.rmtree(PRE_PROCESSING_IN, ignore_errors=True)
#         for value in [start, end]:
#             path = CloudPath(f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/{value}")
#             dir_path = Path(PRE_PROCESSING_IN)
#             dir_path.mkdir(parents=True, exist_ok=True)
#             path.download_to(f"{dir_path}/{value}")

#         return True
#     except Exception as e:
#         print(f"Error in the download_dataset, {e}")
#         return False

# def split_dateset(ratio):
#     try:
#         if os.path.exists(PRE_PROCESSING_OUT):
#             shutil.rmtree(PRE_PROCESSING_OUT, ignore_errors=True)

#         splitfolders.ratio(
#             PRE_PROCESSING_IN,
#             output=PRE_PROCESSING_OUT,
#             seed=0,
#             ratio=ratio, #(0.8, 0, 0.2)
#             group_prefix=None,
#             move=False,
#         )

#         return True
#     except Exception as e:
#         print(f"Error in the split_dateset, {e}")
#         return False


def split_dateset_docker(ratio):
    try:
        path = CloudPath(f's3://{S3_SIG_BUCKET}/data/')
        path.rmtree()
        path.mkdir(exist_ok=True)
        print("Successfully created directories")

        print(PRE_PROCESSING_IN, PRE_PROCESSING_OUT)

        PRE_PROCESSING_IN.mkdir(parents=True, exist_ok=True)
        PRE_PROCESSING_OUT.mkdir(parents=True, exist_ok=True)

        splitfolders.ratio(
            PRE_PROCESSING_IN,
            output=PRE_PROCESSING_OUT,
            seed=0,
            ratio=ratio,  # (0.8, 0, 0.2)
            group_prefix=None,
            move=False,
        )

        path.upload_from(str(PRE_PROCESSING_OUT), force_overwrite_to_cloud=True)
        print("Successfully uploaded directories")
        return True
    except Exception as e:
        print(f"Error in the split_dateset, {e}")
        return False


if __name__ == "__main__":
    split_dateset_docker((0.8, 0, 0.2))
