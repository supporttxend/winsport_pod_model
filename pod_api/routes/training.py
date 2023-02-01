import sagemaker
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Security, status

from pipeline import pipeline

router = APIRouter()


def start_pipline():
    pipeline.create(
        role_arn=sagemaker.get_execution_role(), description="local pipeline example"
    )

    print("running pipline from here")
    execution = pipeline.start()
    steps = execution.list_steps()


@router.get("")
def train(bg_task: BackgroundTasks):
    bg_task.add_task(start_pipline)
    return {"status": status.HTTP_200_OK, "data": "max_index", "feature": "feature"}
