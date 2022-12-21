import boto3
from fastapi import UploadFile
from datetime import datetime
import os
from botocore.exceptions import ClientError


from config import settings


import boto3
from botocore.client import BaseClient

from config import settings
from cloudpathlib import CloudPath
from pathlib import Path


folder = settings.S3_SIG_FOLDER
bucket = settings.S3_SIG_BUCKET

RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER


def s3_auth():
    s3 = boto3.client(
        service_name="s3",
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )
    return s3


def s3_resource():
    s3r = boto3.resource(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    )
    bucket = s3r.Bucket(settings.S3_SIG_BUCKET)
    return bucket


async def upload_file_to_bucket(s3_client, user_id: str, file_obj, object_name=None):
    """Upload a file to an S3 bucket
    :param file_obj: File to upload
    :param bucket: Bucket to upload to
    :param folder: Folder to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_obj
    file_name, file_extension = os.path.splitext(object_name)
    URL = f"{folder}/{user_id}/{user_id}_{file_name}_{datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')}{file_extension}"
    print(URL)

    # Upload the file
    try:
        response = s3_client.upload_fileobj(file_obj, bucket, URL)
    except ClientError as e:
        print(e)
        return False
    return True


def downlaod_data_set():

    try:
        path = CloudPath(f"s3://{bucket}/{folder}")
        dir_path = Path(RAW_DATA_FOLDER)
        dir_path.mkdir(parents=True, exist_ok=True)
        path.download_to(dir_path)

        return True
    except Exception as e:
        print(f"Error in read_images_s3, {e}")
        return False

