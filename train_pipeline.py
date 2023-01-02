import boto3
import sagemaker
from sagemaker.s3 import S3Uploader
from sagemaker.tensorflow import TensorFlow
from sagemaker.estimator import Estimator
from cloudpathlib import CloudPath
from sagemaker.workflow.pipeline_context import PipelineSession

from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.tensorflow import TensorFlowProcessor

from pathlib import Path
import os
from decouple import AutoConfig
from sagemaker.inputs import TrainingInput
from sagemaker.workflow.steps import TrainingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import ProcessingStep

# import code.settings as settings
from processing_pipeline import pipe_line_session

try:
    BASE_DIR = Path(__file__).resolve().parent

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()

print(BASE_DIR)

config = AutoConfig(search_path=BASE_DIR / "code" / "settings.ini")

S3_SIG_BUCKET = config("S3_SIG_BUCKET")
S3_SIG_FOLDER = config("S3_SIG_FOLDER")
RAW_DATA_FOLDER = config("RAW_DATA_FOLDER")
DATA_SET_FOLDER = config("DATA_SET_FOLDER")


print("ENVIORNMENT ----------->", config("ENVIORNMENT"))

# sagemaker_session = sagemaker.Session()

BUCKET_NAME = pipe_line_session.default_bucket()

role = sagemaker.get_execution_role()


model_path = f"s3://{BUCKET_NAME}/models"

# estimator = Estimator(image_uri="train:latest",
#                       role=role,
#                       instance_count=1,
#                       instance_type='local',
#                       source_dir="code",
#                       entry_point="train.py",
#                       output_path=model_path
#                       )

tf_estimator = TensorFlow(
    image_uri="train:latest",
    role=role,
    instance_count=1,
    instance_type="local",
    source_dir="code",
    entry_point="train.py",
    model_dir=model_path,
    framework_version="2.10",
    hyperparameters={"epoch": 2, "batch_size": 128},
    py_version="py39",
    sagemaker_session=pipe_line_session,
)

# train_path =  "test_dir/input/data/train"
# test_path = "test_dir/input/data/test"


if __name__ == "__main__":
    inputs = {
        "train": f"s3://{S3_SIG_BUCKET}/data/train",
        "test": f"s3://{S3_SIG_BUCKET}/data/test",
    }

    tf_estimator.fit(inputs, wait=True, logs="All", job_name="Training")
