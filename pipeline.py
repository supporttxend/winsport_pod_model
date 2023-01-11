import os
import time
from pathlib import Path

import boto3
import sagemaker
from decouple import AutoConfig
from code.config import settings
from sagemaker.inputs import TrainingInput
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import (LocalPipelineSession,
                                                 PipelineSession)
from sagemaker.workflow.steps import ProcessingStep, TrainingStep

from pod_pipeline.processing_pipeline import pipe_line_session, tf_processor
from pod_pipeline.train_pipeline import tf_estimator

try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:
    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

# config = AutoConfig(search_path=BASE_DIR / "code" / "settings.ini")

S3_SIG_BUCKET = settings.S3_SIG_BUCKET
S3_SIG_FOLDER = settings.S3_SIG_FOLDER
RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER


print("ENVIORNMENT ----------->", settings.ENV)

sagemaker_session=sagemaker.Session()

BUCKET_NAME=sagemaker_session.default_bucket()

inputs = [
    ProcessingInput(
        input_name=f"{S3_SIG_FOLDER}",
        source=f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/",
        destination=f"/opt/ml/processing/input/data",
    )
]

output = f's3://{S3_SIG_BUCKET}/data/'


# processor = tf_processor.run(inputs=inputs,code='preprocessing.py',source_dir='code')
# pipeline for data set spliting
step_process = ProcessingStep(
    name="data-spliting",
    step_args=tf_processor.run(
        inputs=inputs,
        code="preprocessing.py",
        source_dir="code",
        wait=True,
    ),
)


estimator = tf_estimator.fit(
    inputs={
        "train": f"s3://{S3_SIG_BUCKET}/data/train",
        "test": f"s3://{S3_SIG_BUCKET}/data/test",
    },
    wait=True,
    logs="All",
    job_name="Training",
)

step_train=TrainingStep(
    name="pod-train-model",
    step_args=estimator,
)

step_train.add_depends_on([step_process])

pipeline=Pipeline(
    name=f"pod-pipeline-dev-{int(time.time())}",
    steps=[step_process, step_train],
    sagemaker_session=pipe_line_session,
)

pipeline.create(
    role_arn=sagemaker.get_execution_role(), description="dev pipeline example"
)

# // pipeline will execute locally
execution=pipeline.start()
steps = execution.list_steps()
print(steps)
