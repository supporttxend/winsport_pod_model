from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Security, status

from pipeline import main_pipeline
from routes.quries_s3 import move_files_s3tos3, empty_s3_folder
from config import settings
import sagemaker
import boto3

from deploy_model import deploy_main


router = APIRouter()

S3_BUCKET_NODE = settings.S3_BUCKET_NODE
S3_SIGNATURE_BUCKET = settings.S3_SIGNATURE_BUCKET
S3_DATA_SET_FOLDER = settings.S3_DATA_SET_FOLDER
S3_PREPARED_DATASET = settings.S3_PREPARED_DATASET


def start_pipline(START_FOLDER,END_FOLDER):


    empty_s3_folder(bucket_name=S3_SIGNATURE_BUCKET, folder_name=S3_DATA_SET_FOLDER)
    empty_s3_folder(bucket_name=S3_SIGNATURE_BUCKET, folder_name=S3_PREPARED_DATASET)
    move_files_s3tos3(START_FOLDER,END_FOLDER, S3_SIGNATURE_BUCKET)

    main_pipeline()



@router.get("/train")
def train(bg_task: BackgroundTasks, START_FOLDER:int =1, END_FOLDER:int=5):
    # bg_task.add_task(start_pipline)
    start_pipline(START_FOLDER,END_FOLDER)
    return {"status": status.HTTP_200_OK, "data": "max_index", "feature": "feature"}



@router.get("/deploy")
def train():
    # bg_task.add_task(start_pipline)
    deploy_main()
    return {"status": status.HTTP_200_OK, "data": "max_index", "feature": "feature"}