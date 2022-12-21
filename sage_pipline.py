import boto3
import sagemaker, boto3, json
from sagemaker import get_execution_role
from config import settings
from quries import downlaod_data_set
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.tensorflow import TensorFlowProcessor


from sagemaker.tensorflow import TensorFlow

RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
folder = settings.S3_SIG_FOLDER
bucket = settings.S3_SIG_BUCKET

try:
    sagemaker_role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    sagemaker_role = iam.get_role(RoleName='<sagemaker-IAM-role-name>')['Role']['Arn']


tf_estimator = TensorFlow(
    entry_point="training.py",
    role='arn:aws:iam::401823493276:role/umar',
    instance_count=1,
    instance_type="ml.m5.4xlarge",
    framework_version="2.10",
    py_version="py39",
    script_mode=True,
)
inputs = {"training": f"s3://{bucket}/{folder}/"}

tf_estimator.fit(inputs)

