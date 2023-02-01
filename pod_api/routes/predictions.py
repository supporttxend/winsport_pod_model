import io
import json
from typing import Union

import numpy as np
import requests
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Security,
    status,
)
from keras.applications.vgg16 import preprocess_input
from pydantic import BaseModel, Field

# from keras.preprocessing import image
from routes.quries_s3 import get_s3_object
from sagemaker.predictor import Predictor
from sqlalchemy.orm import Session
from tensorflow.keras.preprocessing import image

endpoint_name = "pod-endpoint-production-2023-01-30-10-55-37"

router = APIRouter()


def process_s3_image(s3_key):
    # s3_key = "a837a8d7-f9bf-42b8-9af0-9897cfc59fc4/bol/a9310a92-c4bf-4f7f-a169-b4d8a245fc52.jpeg"
    byte_image = get_s3_object(s3_key)
    io_obj = io.BytesIO(byte_image.read())
    raw_image = image.load_img(io_obj, target_size=(224, 224))
    image_array = preprocess_input(
        np.expand_dims(image.img_to_array(raw_image), axis=0)
    )
    input_data = {
        "instances": image_array.tolist(),
    }
    data = json.dumps(input_data)

    return data


@router.get("/")
def get_prediciton(
    image_path: Union[str, None] = Query(
        default="a837a8d7-f9bf-42b8-9af0-9897cfc59fc4/bol/a9310a92-c4bf-4f7f-a169-b4d8a245fc52.jpeg",
        alias="image-path",
    ),
):
    try:
        if not image_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image path can't be empty",
            )

        data = process_s3_image(image_path)
        json_response = requests.post(
            "http://localhost:8080/invocations",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        feature = json_response.json()["predictions"]
        list_1 = feature[0]
        max_value = max(list_1)
        max_index = list_1.index(max_value)
        print(max_index)
        return {"status": status.HTTP_200_OK, "data": max_index, "feature": feature}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error due to {e}",
        )
