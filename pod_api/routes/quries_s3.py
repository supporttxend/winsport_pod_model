import io
from urllib.parse import urlparse

import boto3

from config import settings

S3_BUCKET_NODE = settings.S3_BUCKET_NODE



def connect_bucket():
    s3 = boto3.resource('s3', region_name='us-east-1')
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
    if response['ResponseMetadata']['HTTPStatusCode'] == 204:
        print("object deleted scussfully")
        return
    else:
        print("Error: del_s3_object object is not deleted for {s3_key}")
        return


def get_s3_object(s3_key):
    bucket = connect_bucket()
    response = bucket.Object(s3_key).get()
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        data = response['Body']

        return data
    else:
        print("Error: get_s3_object object is not retrived for {s3_key}")
        return


def get_s3_object_url(s3_key):
    client = boto3.client('s3')
    response = client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET_NODE,'Key': s3_key})
    pasred = urlparse(response)
    public_url = f"{pasred.scheme}://{pasred.hostname}{pasred.path}"

    return public_url