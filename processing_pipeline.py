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
from sagemaker.processing import Processor
from sagemaker.processing import ScriptProcessor
from sagemaker.workflow.pipeline_context import LocalPipelineSession

pipe_line_session = LocalPipelineSession()

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

sagemaker_session = sagemaker.Session()

BUCKET_NAME = sagemaker_session.default_bucket()


role = sagemaker.get_execution_role()

if config("ENVIORNMENT") == 'testing':
    image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/process:latest"
    instance_type = "local"
    pipe_line_session = LocalPipelineSession()

elif config("ENVIORNMENT") == "production":
    image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/process:latest"
    instance_type = "ml.t3.xlarge"
    pipe_line_session = PipelineSession()


tf_processor = TensorFlowProcessor(
    image_uri=image_uri,
    role=role,
    instance_type=instance_type, #"ml.t3.xlarge",
    instance_count=1,
    base_job_name="DataSetSpliting",
    framework_version="2.10",
    # py_version="py39",
    # entrypoint='python preprocessing.py',
    sagemaker_session=pipe_line_session,
)


# if __name__ == "__main__":
#     #Run the processing job
#     # try:
#         tf_processor.run(
#             code='preprocessing.py',
#             source_dir='code',
#             inputs=[
#                 ProcessingInput(
#                     # input_name='data',
#                     source=f's3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/',
#                     destination=f'/opt/ml/processing/input/data'
#                 )
#             ],
#             # outputs=[
#             #     ProcessingOutput(
#             #         # output_name='data',
#             #         source=f"/opt/ml/processing/output",
#             #         # destination=f's3://{S3_SIG_BUCKET}/data',
#             #         # s3_upload_mode="EndOfJob",
#             #     )
#             # ],
#         )
#     # except Exception as e:
#     #     print(e)
