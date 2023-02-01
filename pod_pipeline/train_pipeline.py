import datetime
import os
from code.config import settings
from pathlib import Path

import sagemaker
from decouple import AutoConfig
from sagemaker.tensorflow import TensorFlow, TensorFlowModel

# import code.settings as settings
from pod_pipeline.processing_pipeline import pipe_line_session

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute().parent
    print("Except BASE", BASE_DIR)


# config = AutoConfig(search_path=BASE_DIR / "code" / "settings.ini")

S3_SIG_BUCKET = settings.S3_SIG_BUCKET
S3_SIG_FOLDER = settings.S3_SIG_FOLDER
RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
# PIPE_LINE_SESSION = settings.PIPE_LINE_SESSION


# print("ENVIORNMENT ----------->", config("ENVIORNMENT"))

sagemaker_session = sagemaker.Session()

BUCKET_NAME = sagemaker_session.default_bucket()

role = sagemaker.get_execution_role()


if settings.ENV == "testing":
    base_job_name = (
        f"training-estimator-test-{int(datetime.datetime.now().timestamp())}"
    )
    if settings.DOCKER:
        image_uri = "train:latest"
        source_dir = str(BASE_DIR / "code")

        model_dir = f"s3://{BUCKET_NAME}/{base_job_name}/model"
    else:
        image_uri = False
        source_dir = str(BASE_DIR / "code")
        model_dir = False

    instance_type = "local"
    checkpoint_s3_bucket = False


elif settings.ENV == "production":
    if settings.DOCKER:
        image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/train:latest"
        source_dir = "code"
    else:
        image_uri = False
        source_dir = str(BASE_DIR / "code")

    instance_type = "ml.m5.4xlarge"
    base_job_name = f"training-estimator-production"
    checkpoint_s3_bucket = f"s3://{BUCKET_NAME}/{base_job_name}/checkpoints"


# model_path = f"s3://{BUCKET_NAME}/model"

# tf_estimator = TensorFlow(
#     # image_uri=image_uri,
#     role=role,
#     instance_count=1,
#     instance_type="ml.c5.4xlarge",
#     source_dir=source_dir,
#     entry_point="train.py",
#     model_dir=model_dir,
#     framework_version="2.10",
#     hyperparameters={"epoch": 1, "batch_size": 1, "learning_rate": 0.001},
#     py_version="py39",
#     checkpoint_s3_uri=checkpoint_s3_bucket,
#     # sagemaker_session=sagemaker_session,
#     script_mode=True,
# )

tf_estimator = TensorFlow(
    # image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type="ml.c5.4xlarge",
    source_dir=str(BASE_DIR / "code"),
    entry_point="train.py",
    # model_dir=f"s3://{BUCKET_NAME}/pod-training-step/model",
    framework_version="2.10",
    hyperparameters={"epoch": 1, "batch_size": 1, "learning_rate": 0.001},
    py_version="py39",
    # sagemaker_session=sagemaker_session,
    # script_mode=True,
)


if __name__ == "__main__":
    tf_estimator.fit(
        inputs={
            "train": f"s3://{S3_SIG_BUCKET}/data/train",
            "test": f"s3://{S3_SIG_BUCKET}/data/test",
        },
        wait=True,
        logs="All",
        job_name=base_job_name,
    )

#     tf_model_info = tf_estimator.latest_training_job.describe()
#     model_s3_uri = tf_model_info['ModelArtifacts']['S3ModelArtifacts']

#     predictor = tf_estimator.deploy(
#     initial_instance_count=1,
#     instance_type='local',
#     endpoint_name="test-pod"
#     )


# tf_estimator.create_model(role=role, entry_point='serve.py', source_dir=source_dir)
# tf_estimator.deploy(1, "local", endpoint_name="invocations")
