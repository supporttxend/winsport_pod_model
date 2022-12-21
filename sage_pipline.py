import boto3
import sagemaker, boto3, json
from sagemaker import get_execution_role
from config import settings
from quries import downlaod_data_set
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.tensorflow import TensorFlowProcessor


from sagemaker.tensorflow import TensorFlow

tf_estimator = TensorFlow(
    entry_point="training.py",
    role=get_execution_role(),
    instance_count=1,
    instance_type="local",
    framework_version="2.10",
    py_version="py39",
    script_mode=True,
)
inputs = {"training": f"file://data_set"}

tf_estimator.fit(inputs)

