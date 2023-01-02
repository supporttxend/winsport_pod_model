from pathlib import Path
import os
from decouple import AutoConfig
import boto3
import sagemaker
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.pipeline_context import PipelineSession

from sagemaker.inputs import TrainingInput
from sagemaker.workflow.steps import TrainingStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession

from processing_pipeline import tf_processor, pipe_line_session
from train_pipeline import tf_estimator

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

# pipe_line_session = LocalPipelineSession()


inputs = [
    ProcessingInput(
        input_name="data",
        source=f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/",
        destination=f"/opt/ml/processing/input/data",
    )
]

outputs = [
        ProcessingOutput(
            output_name="data",
            source=f"/opt/ml/processing/output",
            destination=f"s3://{S3_SIG_BUCKET}/data",
            # s3_upload_mode="EndOfJob",
        )
]

# output = f's3://{S3_SIG_BUCKET}/data/'


# processor = tf_processor.run(inputs=inputs,code='preprocessing.py',source_dir='code')
# pipeline for data set spliting
step_process = ProcessingStep(
    name="data-spliting",
    step_args=tf_processor.run(
        inputs=inputs,
        outputs=outputs,
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

step_train = TrainingStep(
    name="TrainPodModel",
    step_args=estimator,
)


pipeline = Pipeline(
    name="POD pipeline",
    steps=[step_process],
    sagemaker_session=pipe_line_session,
)

pipeline.create(
    role_arn=sagemaker.get_execution_role(), description="local pipeline example"
)

# // pipeline will execute locally
execution = pipeline.start()
steps = execution.list_steps()
print(steps)
