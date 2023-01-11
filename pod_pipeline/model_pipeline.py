from sagemaker.tensorflow import TensorFlowModel
import sagemaker
from sagemaker.model import Model
from code.config import settings
from pathlib import Path


try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute().parent
    print("Except BASE", BASE_DIR)

sagemaker_session = sagemaker.Session()

BUCKET_NAME = sagemaker_session.default_bucket()

role = sagemaker.get_execution_role()


if settings.ENV == 'testing':
    base_job_name = f"training-estimator-test"
    if settings.DOCKER:
        image_uri = "train:latest"
        source_dir= str(BASE_DIR / 'code')

        model_dir= f"s3://{BUCKET_NAME}/{base_job_name}/model"
    else:
        image_uri=False
        source_dir= str(BASE_DIR / 'code')
        model_dir=False

    instance_type = "local"
    checkpoint_s3_bucket=False


elif settings.ENV == "production":
    if settings.DOCKER:
        image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/train:latest"
        source_dir = "code"
    else:
        image_uri = False
        source_dir=str(BASE_DIR / 'code')

    instance_type = "ml.m5.4xlarge"
    base_job_name = f"training-estimator-production"
    checkpoint_s3_bucket=f"s3://{BUCKET_NAME}/{base_job_name}/checkpoints"


model = TensorFlowModel(
    # image_uri="train:latest",
    model_data=f"s3://sagemaker-us-west-1-401823493276/training-estimator-test/model.tar.gz",
    role=role,
    source_dir=source_dir,
    entry_point="inference.py",
    framework_version="2.10"
    )



predictor = model.deploy(
    initial_instance_count=1,
    instance_type='local',
    endpoint_name="test-pod"
    )