from pod_model import settings
import boto3
import sagemaker
from sagemaker.s3 import S3Uploader
from sagemaker.tensorflow import TensorFlow
from sagemaker.estimator import Estimator



RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
S3_SIG_FOLDER = settings.S3_SIG_FOLDER
S3_SIG_BUCKET = settings.S3_SIG_BUCKET


#Uploading data to S3 bucket titled "tf-iris-data"

DESTINATION_FOLDER = f"s3://{S3_SIG_BUCKET}/data-set/"


prefix = "pod-data"
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()

# tf_estimator = Estimator(image_uri="401823493276.dkr.ecr.us-east-1.amazonaws.com/pod:latest",
#                          entry_point='train.py',
#                           role=role,
#                           instance_type='local',
#                           source_dir="pod_model",
#                          )

#Training


# training_input_path = sagemaker_session.upload_data(path="pod_model/data_set")
# print(training_input_path)
# tf_estimator.fit()

from sagemaker.estimator import Estimator

estimator = Estimator(image_uri="401823493276.dkr.ecr.us-east-1.amazonaws.com/pod:latest",
                      role=role,
                      instance_count=2,
                      instance_type="ml.m5.xlarge",
                      entry_point='train.py',
                      source_dir="pod_model"
                      )

estimator.fit()
