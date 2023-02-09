import argparse
import boto3
import logging
import os
from botocore.exceptions import ClientError
import tarfile
import zipfile
import subprocess

logger = logging.getLogger(__name__)
sm_client = boto3.client("sagemaker")
s3_client  = boto3.client("s3")


def get_approved_package(model_package_group_name):
    """Gets the latest approved model package for a model package group.

    Args:
        model_package_group_name: The model package group name.

    Returns:
        The SageMaker Model Package ARN.
    """
    try:
        # Get the latest approved model package
        response = sm_client.list_model_packages(
            ModelPackageGroupName=model_package_group_name,
            ModelApprovalStatus="Approved",
            SortBy="CreationTime",
            MaxResults=100,
        )
        approved_packages = response["ModelPackageSummaryList"]

        # Fetch more packages if none returned with continuation token
        while len(approved_packages) == 0 and "NextToken" in response:
            logger.debug("Getting more packages for token: {}".format(response["NextToken"]))
            response = sm_client.list_model_packages(
                ModelPackageGroupName=model_package_group_name,
                ModelApprovalStatus="Approved",
                SortBy="CreationTime",
                MaxResults=100,
                NextToken=response["NextToken"],
            )
            approved_packages.extend(response["ModelPackageSummaryList"])

        # Return error if no packages found
        if len(approved_packages) == 0:
            error_message = (
                f"No approved ModelPackage found for ModelPackageGroup: {model_package_group_name}"
            )
            logger.error(error_message)
            raise Exception(error_message)

        # Return the pmodel package arn
        model_package_arn = approved_packages[0]["ModelPackageArn"]
        logger.info(f"Identified the latest approved model package: {model_package_arn}")
        return approved_packages[0]
        # return model_package_arn
    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        logger.error(error_message)
        raise Exception(error_message)


def get_model_artificates():
    return sm_client.list_artifacts(SortBy="CreationTime")['ArtifactSummaries'][0]['Source']['SourceUri']



def get_model_package_groups_name():
    model_groups = sm_client.list_model_package_groups(
        SortBy="CreationTime", #'Name'|'CreationTime',
        SortOrder="Descending" #'Ascending'|'Descending'
    )

    if model_groups['ModelPackageGroupSummaryList']:
        return model_groups['ModelPackageGroupSummaryList'][0]['ModelPackageGroupName']
    else:
       sm_client.create_model_package_group(
            ModelPackageGroupName='pod-model-packages',
            ModelPackageGroupDescription='pod-model-packages discription',
            )
       return get_model_package_groups_name()



def get_or_create_models(model_name, model_description, role):
    paginator = sm_client.get_paginator('list_models')

    response_iterator = paginator.paginate(
            SortBy='CreationTime',
            SortOrder='Descending',
            NameContains=model_name,
        )
    if response_iterator.build_full_result()['Models']:
        print(f"model for this name '{model_name}' already exsists....!")
        return False
    else:
        create_model_response = sm_client.create_model(
            ModelName = model_name,
            ExecutionRoleArn = role,
            PrimaryContainer = {
                "Image": model_description['InferenceSpecification']['Containers'][0]['Image'],
                'ModelDataUrl': model_description['InferenceSpecification']['Containers'][0]['ModelDataUrl'],
            })
        return True


def get_or_ep_config(model_name):
    paginator = sm_client.get_paginator('list_endpoint_configs')

    new_endpoint_config_name = f'pod-endpoint-configs-{model_name}'

    model_varient = '-'.join(model_name.split('-')[-2:])

    response_iterator = paginator.paginate(
        SortBy='CreationTime',
        SortOrder='Descending',
        NameContains=new_endpoint_config_name,
    )
    if response_iterator.build_full_result()['EndpointConfigs']:
        return response_iterator.build_full_result()['EndpointConfigs'][0]['EndpointConfigName']
    else:
        sm_client.create_endpoint_config(
            EndpointConfigName=new_endpoint_config_name,
            ProductionVariants=[{
                'VariantName': f"{model_varient}",
                'ModelName': model_name,
                'InstanceType': "ml.c5.4xlarge",
                'InitialInstanceCount': 1
            }]
        )
        return get_or_ep_config(model_name)

def create_update_ep(model_name):
    endpoint_name = 'pod-endpoint'
    response = sm_client.list_endpoints()
    model_varient = '-'.join(model_name.split('-')[-2:])
    if response["Endpoints"]:
        ep_response = sm_client.describe_endpoint(
                EndpointName=endpoint_name
            )
        if ep_response['EndpointStatus'] == 'Creating':
            print("end point is in creating mode, please wait .....!")
            return False
        if ep_response['ProductionVariants']:
            print(" here is ProductionVariants")
            if ep_response['ProductionVariants'][0]['VariantName'] == model_varient :
                print(f"end point is already created and attached to model {model_name, model_varient}")
                return False
            else:
                print(f"end point is already created and update to model {model_name, model_varient}")
                response = sm_client.update_endpoint(
                    EndpointName=endpoint_name,
                    EndpointConfigName=get_or_ep_config(model_name)
                )

                try:
                    sm_client.get_waiter("endpoint_in_service").wait(EndpointName=endpoint_name)
                finally:
                    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
                    status = resp["EndpointStatus"]
                    print("Arn: " + resp["EndpointArn"])
                    print("updating endpoint ended with status: " + status)

                    if status != "InService":
                        message = sm_client.describe_endpoint(EndpointName=endpoint_name)["FailureReason"]
                        print("Updating failed with the following error: {}".format(message))
                        raise Exception("Endpoint creation did not succeed")
                return response

        else:
            return
    else:
        response = sm_client.create_endpoint(
                    EndpointName=endpoint_name,
                    EndpointConfigName=get_or_ep_config(model_name)
                )

        try:
            sm_client.get_waiter("endpoint_in_service").wait(EndpointName=endpoint_name)
        finally:
            resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
            status = resp["EndpointStatus"]
            print("Arn: " + resp["EndpointArn"])
            print("Create endpoint ended with status: " + status)

            if status != "InService":
                message = sm_client.describe_endpoint(EndpointName=endpoint_name)["FailureReason"]
                print("Training failed with the following error: {}".format(message))
                raise Exception("Endpoint creation did not succeed")

        return response