import datetime
import os
import time
from config import settings
from pathlib import Path

import boto3
import sagemaker
from sagemaker import PipelineModel, image_uris
from sagemaker.inputs import CreateModelInput, TrainingInput
from sagemaker.model import Model
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.tensorflow import TensorFlow, TensorFlowModel, TensorFlowProcessor
from sagemaker.workflow.model_step import CreateModelStep, ModelStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession, PipelineSession
from sagemaker.workflow.retry import (
    SageMakerJobExceptionTypeEnum,
    SageMakerJobStepRetryPolicy,
    StepExceptionTypeEnum,
    StepRetryPolicy,
)
from sagemaker.workflow.steps import ProcessingStep, TrainingStep

# from pod_pipeline.model_pipeline import model
from pod_pipeline.utils import get_approved_package, get_model_package_groups_name

# from pod_pipeline.processing_pipeline import tf_processor
# from pod_pipeline.train_pipeline import tf_estimator

try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:
    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

local_pipeline_session = PipelineSession()  # LocalPipelineSession()

S3_SIGNATURE_BUCKET = settings.S3_SIGNATURE_BUCKET
S3_DATA_SET_FOLDER = settings.S3_DATA_SET_FOLDER
S3_PREPARED_DATASET = settings.S3_PREPARED_DATASET
PRE_PROCESSING_IN = settings.PRE_PROCESSING_IN
PRE_PROCESSING_OUT = settings.PRE_PROCESSING_OUT
INSTANCE_TYPE = settings.INSTANCE_TYPE
APPROVAL_STATUS = settings.APPROVAL_STATUS

BUCKET_NAME = local_pipeline_session.default_bucket()

role = sagemaker.get_execution_role()

model_package_group_name = get_model_package_groups_name()

try:
    pck = get_approved_package(get_model_package_groups_name())
    version = int(pck["ModelPackageArn"].split("/")[-1]) + 1

except:
    version = 1


# %% Data Spliting pipeline


def define_pipeline():

    # %% Create step for data set spliting

    inputs = [
        ProcessingInput(
            # input_name=f"{S3_SIG_FOLDER}",
            source=f"s3://{S3_SIGNATURE_BUCKET}/{S3_DATA_SET_FOLDER}/",
            destination=f"{PRE_PROCESSING_IN}",
        )
    ]
    output = [
        ProcessingOutput(
            source=f"{PRE_PROCESSING_OUT}",
            destination=f"s3://{S3_SIGNATURE_BUCKET}/{S3_PREPARED_DATASET}/",
            # s3_upload_mode="EndOfJob"
        )
    ]

    tf_processor = TensorFlowProcessor(
        role=role,
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        base_job_name=f"data-spliting-processor-testing-{datetime.datetime.now().strftime('%d_%B_%Y_%H_%M_%S_%p')}",
        framework_version="2.10",
        py_version="py39",
        sagemaker_session=local_pipeline_session,
        env={"TRAIN": "0.7", "VALID":"0", "TEST":"0.3"}
    )

    processor = tf_processor.run(
            code="preprocessing.py",inputs=inputs, wait=True, logs= True, outputs=output, source_dir=str(BASE_DIR / "wrangal")
        )
    step_process = ProcessingStep(
        name="pod-preprocessing-step",
        step_args=processor,
        inputs=inputs
    )

    print("easily crossed the processing step")

    # %% Training Input and Training steps defination
    train = TrainingInput(f"s3://{S3_SIGNATURE_BUCKET}/{S3_PREPARED_DATASET}/train")
    test = TrainingInput(f"s3://{S3_SIGNATURE_BUCKET}/{S3_PREPARED_DATASET}/test")

    tf_estimator = TensorFlow(
        role=role,
        instance_count=1,
        instance_type=INSTANCE_TYPE,
        source_dir=str(BASE_DIR / "code"),
        entry_point="train.py",
        framework_version="2.10",
        hyperparameters={"epoch": 1, "batch_size": 1, "learning_rate": 0.001},
        py_version="py39",
    )

    step_train = TrainingStep(
        name="pod-training-step",
        estimator=tf_estimator,
        inputs={"train": train, "test": test},
        retry_policies=[
            # retry when resource limit quota gets exceeded
            SageMakerJobStepRetryPolicy(
                exception_types=[SageMakerJobExceptionTypeEnum.RESOURCE_LIMIT],
                expire_after_mins=120,
                interval_seconds=60,
                backoff_rate=2.0,
            )
        ],
    )

    print("easily crossed the training step")

    # %% Model Registration step

    model = TensorFlowModel(
        # image_uri=tf_estimator.training_image_uri(),
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        role=role,
        source_dir=str(BASE_DIR / "code"),
        entry_point="inference.py",
        framework_version="2.10",
        sagemaker_session=local_pipeline_session,
    )

    pipeline_model = PipelineModel(
        models=[model],
        role=role,
        sagemaker_session=local_pipeline_session,
        name=f"pod-model-{version}",
    )

    register_args = pipeline_model.register(
        content_types=["*"],
        response_types=["application/json"],
        inference_instances=[INSTANCE_TYPE],
        transform_instances=[INSTANCE_TYPE],
        model_package_group_name=model_package_group_name,
        approval_status=APPROVAL_STATUS,
    )

    print("easily crossed the register step")

    step_register_pipeline_model = ModelStep(
        name="PipelineModel",
        step_args=register_args,
    )

    step_train.add_depends_on([step_process])
    # model_step.add_depends_on([step_train])
    pipeline = Pipeline(
        name=f"pod-pipeline-dev-{int(datetime.datetime.now().timestamp())}",
        steps=[step_process, step_train, step_register_pipeline_model], #step_train, step_register_pipeline_model
        sagemaker_session=local_pipeline_session,
    )

    return pipeline


def run_pipeline(pipeline):

    pipeline.upsert(
        role_arn=sagemaker.get_execution_role(), description="local pipeline example"
    )

    # execution = pipeline.create(
    #     role_arn=sagemaker.get_execution_role(), description="local pipeline example"
    # )

    execution = pipeline.start()
    print("running pipline from here")

    execution.wait()

    return execution, pipeline


def stop_pipeline(execution):
    execution.stop()

    return execution


def delete_pipeline(pipeline):
    pipeline.delete()

    return pipeline

def main_pipeline():
    pipeline = define_pipeline()
    execution, pipeline = run_pipeline(pipeline)

    for step in execution.list_steps():
        if step['StepStatus'] == 'Succeeded':
            print(f"Step = {step['StepName']} run successfully and status is = {step['StepStatus']}")
        else:
            raise Exception(f"Pipeline failed at this step = {step['StepName']} haveing status = {step['StepStatus']}")

    return True





if __name__ == "__main__":
    print("not load on import")
    main_pipeline()

    # execution = pipeline.start()

    # steps = execution.list_steps()
