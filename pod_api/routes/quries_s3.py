import io
from urllib.parse import urlparse

import boto3
from config import settings
import subprocess

S3_BUCKET_NODE = settings.S3_BUCKET_NODE


def connect_bucket():
    s3 = boto3.resource("s3", region_name="us-east-1")
    bucket = s3.Bucket(S3_BUCKET_NODE)
    return bucket


def upload_image_to_s3(image, s3_key):
    io_obj = io.BytesIO()
    image.save(io_obj, format="JPEG")
    io_obj.seek(0)

    bucket = connect_bucket()
    bucket.upload_fileobj(io_obj, s3_key)

    return


def upload_pdf_to_s3(pdf, s3_key):
    with io.BytesIO() as bytes_stream:
        pdf.write(bytes_stream)
        bytes_stream.seek(0)
        bucket = connect_bucket()
        bucket.upload_fileobj(bytes_stream, s3_key)


def del_s3_object(s3_key):
    bucket = connect_bucket()
    response = bucket.Object(s3_key).delete()
    if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
        print("object deleted scussfully")
        return
    else:
        print("Error: del_s3_object object is not deleted for {s3_key}")
        return


def get_s3_object(s3_key):
    bucket = connect_bucket()
    response = bucket.Object(s3_key).get()
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        data = response["Body"]

        return data
    else:
        print("Error: get_s3_object object is not retrived for {s3_key}")
        return


def get_s3_object_url(s3_key):
    client = boto3.client("s3")
    response = client.generate_presigned_url(
        "get_object", Params={"Bucket": S3_BUCKET_NODE, "Key": s3_key}
    )
    pasred = urlparse(response)
    public_url = f"{pasred.scheme}://{pasred.hostname}{pasred.path}"

    return public_url


def move_files_s3tos3(START_FOLDER,END_FOLDER, S3_SIG_BUCKET):

    for i in range(START_FOLDER, END_FOLDER+1):
        push=subprocess.call(f'aws s3 cp --recursive s3://{S3_SIG_BUCKET}/signatures/{i}  s3://{S3_SIG_BUCKET}/dataset/{i}'.split( ))


def delete_folders_s3():
    subprocess.call(f'aws s3 rm s3://winsport-signatures-dev/dataset/* --recursive'.split( ))
    subprocess.call(f'aws s3 rm s3://winsport-signatures-dev/prepared_dataset/ --recursive'.split( ))



def empty_s3_folder(bucket_name='winsport-signatures-dev', folder_name='dataset'):
    s3 = boto3.client('s3')
    """Delete all files in a specific folder in an S3 bucket"""
    # Get a list of all objects in the folder
    result = s3.list_objects(Bucket=bucket_name, Prefix=folder_name)
    # If the folder is not empty
    if 'Contents' in result:
        # Delete all objects in the folder
        objects_to_delete = [{'Key': obj['Key']} for obj in result['Contents']]
        s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
        print(f"Emptied folder {folder_name} in S3 bucket {bucket_name}")
    else:
        print(f"Folder {folder_name} in S3 bucket {bucket_name} is already empty")
