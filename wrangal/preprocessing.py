from pathlib import Path

import splitfolders
import os
import shutil
import subprocess

try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

PRE_PROCESSING_IN = '/opt/ml/processing/input/data'
PRE_PROCESSING_OUT = '/opt/ml/processing/output/'

def split_dateset_docker(SPLIT_RATIOS):
    # try:

        print("Successfully created directories")

        print(PRE_PROCESSING_IN, PRE_PROCESSING_OUT)

        splitfolders.ratio(
            input=PRE_PROCESSING_IN,
            output=PRE_PROCESSING_OUT,
            seed=0,
            ratio=SPLIT_RATIOS,  # (0.8, 0, 0.2)
            group_prefix=None,
            move=False,
        )

        # print("Successfully uploaded directories")
        return True
    # except Exception as e:
    #     print(f"Error in the split_dateset, {e}")
    #     return False


if __name__ == "__main__":
    SPLIT_RATIOS = os.environ.get('SPLIT_RATIOS')
    TRAIN = float(os.environ.get("TRAIN"))
    VALID = float(os.environ.get("VALID"))
    TEST = float(os.environ.get("TEST"))

    print("spliting ration is", TRAIN, VALID, TEST)
    SPLIT_RATIOS = (TRAIN, VALID, TEST)
    split_dateset_docker(SPLIT_RATIOS)
