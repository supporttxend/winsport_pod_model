import datetime
import os
from code.config_temp import settings
from config import settings as api_settings
from pathlib import Path

import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput, Processor
from sagemaker.tensorflow import TensorFlowProcessor
from sagemaker.workflow.pipeline_context import LocalPipelineSession, PipelineSession
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.processing import ScriptProcessor, FrameworkProcessor

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute().parent
    print("Except BASE", BASE_DIR)

# S3_SIG_BUCKET = settings.S3_SIG_BUCKET
# S3_SIG_FOLDER = settings.S3_SIG_FOLDER
# RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
# DATA_SET_FOLDER = settings.DATA_SET_FOLDER

S3_SIGNATURE_BUCKET = api_settings.S3_SIGNATURE_BUCKET
S3_DATA_SET_FOLDER = api_settings.S3_DATA_SET_FOLDER
S3_PREPARED_DATASET = api_settings.S3_PREPARED_DATASET


role = sagemaker.get_execution_role()


# this must be test on the production instance
if settings.ENV == "testing":
    instance_type = "local" #"ml.c5.4xlarge"
    pipe_line_session = False
    base_job_name = f"data-spliting-processor-testing"


elif settings.ENV == "production":
    instance_type = "ml.c5.4xlarge"
    pipe_line_session = PipelineSession()
    base_job_name = f"data-spliting-processor-production-{datetime.datetime.now().strftime('%d_%B_%Y_%H_%M_%S_%p')}"


tf_processor = TensorFlowProcessor(
    role=role,
    instance_type=instance_type,
    instance_count=1,
    base_job_name=base_job_name,
    framework_version="2.10",
    py_version="py39",
    sagemaker_session=pipe_line_session,
    env={"TRAIN": "0.8", "VALID":"0", "TEST":"0.2"}
)



if __name__ == "__main__":
    # Run the processing job

    try:
        inputs = [
            ProcessingInput(
                # input_name=f"{S3_SIG_FOLDER}",
                source=f"s3://{S3_SIGNATURE_BUCKET}/{S3_DATA_SET_FOLDER}/",
                destination=f"/opt/ml/processing/input/data",
            )
        ]
        output = [
            ProcessingOutput(
                source=f"/opt/ml/processing/output/",
                destination=f"s3://{S3_SIGNATURE_BUCKET}/{S3_PREPARED_DATASET}/",
                s3_upload_mode="EndOfJob"
            )
        ]
        tf_processor.run(
            code="preprocessing.py",inputs=inputs, wait=True, logs= True, outputs=output, source_dir=str(BASE_DIR / "wrangal")
        )
    except Exception as e:
        print(e)

        # docker-compose -f /tmp/tmpmrnoupy_/docker-compose.yaml up --build