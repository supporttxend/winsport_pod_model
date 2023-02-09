import boto3
import sagemaker

from pod_pipeline.utils import (
    create_update_ep,
    get_approved_package,
    get_model_package_groups_name,
    get_or_create_models,
    get_or_ep_config,
)

sess = boto3.Session()
sm_client = boto3.client("sagemaker")






def deploy_model(model_name, model_description, role):
    get_or_create_models(model_name, model_description, role)

    get_or_ep_config(model_name)

    create_update_ep(model_name)


def deploy_main():

    pck = get_approved_package(get_model_package_groups_name())
    model_description = sm_client.describe_model_package(
        ModelPackageName=pck["ModelPackageArn"]
    )
    role = sagemaker.get_execution_role()
    model_version = pck["ModelPackageVersion"]
    model_name = f"pod-model-version-{model_version}"

    deploy_model(model_name, model_description, role)


if __name__ == "__main__":
    print("not load on import")

    deploy_main()

