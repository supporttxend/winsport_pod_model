import os
from pathlib import Path

import sagemaker
from decouple import AutoConfig
from code.config import settings
from sagemaker.processing import ProcessingInput, ProcessingOutput, Processor
from sagemaker.tensorflow import TensorFlowProcessor
from sagemaker.workflow.pipeline_context import LocalPipelineSession, PipelineSession
from sagemaker.workflow.steps import ProcessingStep
import datetime

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

# sagemaker_session = sagemaker.Session()

# BUCKET_NAME = sagemaker_session.default_bucket()


role = sagemaker.get_execution_role()

if settings.ENV == "testing":
    # image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/process:latest"
    instance_type = "local"
    pipe_line_session = LocalPipelineSession()
    base_job_name = f"data-spliting-processor-testing-{datetime.datetime.now().strftime('%d_%B_%Y_%H_%M_%S_%p')}"

elif settings.ENV == "production":
    # image_uri = "401823493276.dkr.ecr.us-west-1.amazonaws.com/process:latest"
    instance_type = "ml.t3.xlarge"
    pipe_line_session = PipelineSession()
    base_job_name = f"data-spliting-processor-production-{datetime.datetime.now().strftime('%d_%B_%Y_%H_%M_%S_%p')}"


tf_processor = TensorFlowProcessor(
    # image_uri = image_uri,
    role = role,
    instance_type = instance_type,
    instance_count = 1,
    base_job_name = base_job_name,
    framework_version = "2.10",
    py_version = "py39",
    # code_location=str(BASE_DIR / 'code'),
    # entrypoint = 'python preprocessing.py',
    sagemaker_session = pipe_line_session,
)


if __name__ == "__main__":
        #Run the processing job
    try:
        inputs = [
            ProcessingInput(
                input_name = f"{S3_SIG_FOLDER}",
                source = f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/",
                destination = f"/opt/ml/processing/input/data",
            )
        ]
        tf_processor.run(code = "preprocessing.py", source_dir = str(BASE_DIR / 'code'), inputs = inputs)
    except Exception as e:
        print(e)


#             # outputs=[
#             #     ProcessingOutput(
#             #         # output_name='data',
#             #         source=f"/opt/ml/processing/output",
#             #         # destination=f's3://{S3_SIG_BUCKET}/data',
#             #         # s3_upload_mode="EndOfJob",
#             #     )
#             # ],
