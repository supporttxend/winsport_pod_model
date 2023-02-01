import boto3
import sagemaker
from sagemaker import ModelPackage

from pod_pipeline.utils import (
    create_update_ep,
    get_approved_package,
    get_model_package_groups_name,
    get_or_create_models,
    get_or_ep_config,
)

sess = boto3.Session()
sm_client = boto3.client("sagemaker")

role = sagemaker.get_execution_role()

pck = get_approved_package(get_model_package_groups_name())
model_description = sm_client.describe_model_package(
    ModelPackageName=pck["ModelPackageArn"]
)


sagemaker_session = sagemaker.Session(boto_session=sess)
model_package_arn = model_description["ModelPackageArn"]
# model = ModelPackage(
#     role=role, model_package_arn=model_package_arn, sagemaker_session=sagemaker_session
# )
# model_data = model_description['InferenceSpecification']['Containers'][0]['ModelDataUrl']
# model.image_uri = tf_estimator.training_image_uri()
# model.model_data = model_register_args.model.model_data

# endpoint_name = "DEMO-endpoint-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
# endpoint_name = "pod-endpoint-production-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
# print("EndpointName= {}".format(endpoint_name))
# model.deploy(initial_instance_count=1, instance_type=instance_type, endpoint_name=endpoint_name)


model_version = pck["ModelPackageVersion"]
model_name = f"pod-model-version-{model_version}"


def deploy_model(model_name, model_description, role):
    resp = get_or_create_models(model_name, model_description, role)
    # if not resp:
    #     print("error at model creating")
    #     return
    get_or_ep_config(model_name)

    create_update_ep(model_name)

deploy_model(model_name, model_description, role)
