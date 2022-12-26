
from config import settings
from cloudpathlib import CloudPath
from pathlib import Path
import os
import shutil
import splitfolders


S3_SIG_FOLDER = settings.S3_SIG_FOLDER
S3_SIG_BUCKET = settings.S3_SIG_BUCKET
RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER


def download_dataset(start, end):
    try:
        if os.path.exists(RAW_DATA_FOLDER):
            shutil.rmtree(RAW_DATA_FOLDER, ignore_errors=True)
        for value in [start, end]:
            path = CloudPath(f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/{value}")
            dir_path = Path(RAW_DATA_FOLDER)
            dir_path.mkdir(parents=True, exist_ok=True)
            path.download_to(f"{dir_path}/{value}")

        return True
    except Exception as e:
        print(f"Error in the download_dataset, {e}")
        return False

def split_dateset(ratio):
    try:
        if os.path.exists(DATA_SET_FOLDER):
            shutil.rmtree(DATA_SET_FOLDER, ignore_errors=True)

        splitfolders.ratio(
            RAW_DATA_FOLDER,
            output=DATA_SET_FOLDER,
            seed=0,
            ratio=ratio, #(0.8, 0, 0.2)
            group_prefix=None,
            move=False,
        )

        return True
    except Exception as e:
        print(f"Error in the split_dateset, {e}")
        return False


if __name__ == "__main__":
    try:
        resp = download_dataset(2, 4)
        if resp:
            split_dateset((0.8, 0, 0.2))
    except Exception as e:
        print(f"Error in the main processing, {e}")

