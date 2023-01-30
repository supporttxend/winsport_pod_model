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
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.tensorflow import TensorFlowProcessor
import datetime
from sagemaker.tensorflow import TensorFlow
from sagemaker.workflow.model_step import ModelStep, CreateModelStep
from sagemaker import PipelineModel
from sagemaker.tensorflow import TensorFlowModel
import sagemaker
from sagemaker.model import Model
from pod_pipeline.model_pipeline import model
from sagemaker import image_uris
from sagemaker.workflow.retry import (
    StepRetryPolicy,
    StepExceptionTypeEnum,
    SageMakerJobExceptionTypeEnum,
    SageMakerJobStepRetryPolicy
)
from sagemaker.inputs import CreateModelInput
from sagemaker import PipelineModel

# from pod_pipeline.processing_pipeline import tf_processor
# from pod_pipeline.train_pipeline import tf_estimator

try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:
    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

local_pipeline_session = PipelineSession() #LocalPipelineSession()

S3_SIG_BUCKET = settings.S3_SIG_BUCKET
S3_SIG_FOLDER = settings.S3_SIG_FOLDER
RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER

BUCKET_NAME = local_pipeline_session.default_bucket()

role = sagemaker.get_execution_role()

model_package_group_name = "pod-model-packages"
instance_type = "ml.c5.4xlarge"
approval_status = "Approved"


# image_uri = image_uris.retrieve(framework='tensorflow',region='us-west-1',version='2.10',image_scope='training',instance_type='ml.c5.4xlarge')


# %% Data Spliting pipeline


inputs = [
    ProcessingInput(
        input_name=f"{S3_SIG_FOLDER}",
        source=f"s3://{S3_SIG_BUCKET}/{S3_SIG_FOLDER}/",
        destination=f"/opt/ml/processing/input/data",
    )
]

tf_processor = TensorFlowProcessor(
    role=role,
    instance_type=instance_type,
    instance_count=1,
    base_job_name=f"data-spliting-processor-testing-{datetime.datetime.now().strftime('%d_%B_%Y_%H_%M_%S_%p')}",
    framework_version="2.10",
    py_version="py39",
    sagemaker_session=local_pipeline_session,
)

processor = tf_processor.run(
    code="preprocessing.py", source_dir=str(BASE_DIR / "code"), inputs=inputs
)
step_process = ProcessingStep(
    name="pod-preprocessing-step",
    step_args=processor,
)


print("easily crossed the processing step")


# %% Training Input and Training steps defination
train = TrainingInput(f"s3://{S3_SIG_BUCKET}/data/train")
test = TrainingInput(f"s3://{S3_SIG_BUCKET}/data/test")

tf_estimator = TensorFlow(
    role=role,
    instance_count=1,
    instance_type=instance_type,
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
            backoff_rate=2.0
        )
    ]
)

print("easily crossed the training step")


# %% Model deployment

model = TensorFlowModel(
    # image_uri=tf_estimator.training_image_uri(),
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    role=role,
    source_dir=str(BASE_DIR / "code"),
    entry_point="inference.py",
    framework_version="2.10",
    sagemaker_session=local_pipeline_session,
    )

# model_register_args = model.register(
#     image_uri=tf_estimator.training_image_uri(),
#     approval_status=approval_status,
#     content_types=["*"],
#     response_types=["application/json"],
#     inference_instances=[instance_type],
#     transform_instances=[instance_type],
#     model_package_group_name=model_package_group_name,
#     framework_version="2.10"

#     )


# model_register_step= ModelStep(
#    name="pod-model-register-step",
#    step_args=model_register_args,
#    depends_on=[step_train]
# )



pipeline_model = PipelineModel(
    models=[model], role=role, sagemaker_session=local_pipeline_session
)


register_args = pipeline_model.register(
    content_types=["*"],
    response_types=["application/json"],
    inference_instances=[instance_type],
    transform_instances=[instance_type],
    model_package_group_name=model_package_group_name,
    approval_status=approval_status,
)

step_register_pipeline_model = ModelStep(
    name="PipelineModel",
    step_args=register_args,
)


# %% model create

# model_create_args = model.create(
#     instance_type='ml.c5.4xlarge',
# )

# model_create_step = ModelStep(
#    name="pod-model-create-step",
#    step_args=model_create_args,
# )

# print("easily crossed the model creation step")

# %% model deploy

# predictor = model.deploy(
#     initial_instance_count=1,
#     instance_type='local',
#     endpoint_name="test-pod"
#     )
# endpoint_name = "pod-endpoint-production-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
# print("EndpointName= {}".format(endpoint_name))
# model_deploy_args = model.deploy(
#     instance_type='ml.c5.4xlarge',
#     initial_instance_count=1,
#     endpoint_name=endpoint_name,
# )

# model_deploy_step = ModelStep(
#    name="pod-model-deploy-step",
#    step_args=model_deploy_args,
# )

print("easily crossed the model creation step")
# %% Pipeline defination

step_train.add_depends_on([step_process])
# model_step.add_depends_on([step_train])
pipeline = Pipeline(
    name=f"pod-pipeline-dev-{int(datetime.datetime.now().timestamp())}",
    steps=[step_process, step_train, step_register_pipeline_model],
    sagemaker_session=local_pipeline_session,
)


execution = pipeline.create(
    role_arn=sagemaker.get_execution_role(), description="local pipeline example"
)
print("running pipline from here")

execution = pipeline.start()

# execution = pipeline.upsert(role_arn=role)

steps = execution.list_steps()


from pod_pipeline.utils import get_approved_package
from sagemaker import ModelPackage
sess = boto3.Session()

sm_client = boto3.client("sagemaker")

pck = get_approved_package(
    model_package_group_name
)

model_description = sm_client.describe_model_package(ModelPackageName=pck["ModelPackageArn"])


sagemaker_session = sagemaker.Session(boto_session=sess)
model_package_arn = model_description["ModelPackageArn"]
model = ModelPackage(
    role=role, model_package_arn=model_package_arn, sagemaker_session=sagemaker_session
)
model_data = model_description['InferenceSpecification']['Containers'][0]['ModelDataUrl']
model.image_uri = tf_estimator.training_image_uri()
model.model_data = model_register_args.model.model_data

# endpoint_name = "DEMO-endpoint-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
endpoint_name = "pod-endpoint-production-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
print("EndpointName= {}".format(endpoint_name))
model.deploy(initial_instance_count=1, instance_type=instance_type, endpoint_name=endpoint_name)

# running last hope
# model = TensorFlowModel(
#     # image_uri=tf_estimator.training_image_uri(),
#     model_data=sm_client.list_artifacts(SortBy="CreationTime")['ArtifactSummaries'][0]['Source']['SourceUri'],
#     role=role,
#     source_dir=str(BASE_DIR / "code"),
#     entry_point="inference.py",
#     framework_version="2.10",
#     # sagemaker_session=local_pipeline_session,
#     )

# predictor = model.deploy(
#     initial_instance_count=1,
#     instance_type='ml.c5.4xlarge',
#     endpoint_name="test-pod-123"
#     )





if __name__ == "__main__":
    pass
    # execution = pipeline.start()

    # steps = execution.list_steps()