from fastapi import (
    HTTPException,
    Depends,
    APIRouter,
    status,
    HTTPException,
    Security,
    BackgroundTasks,
    Query
)
from sqlalchemy.orm import Session
from keras.applications.vgg16 import preprocess_input
# from session import get_db
import json
from tensorflow.keras.preprocessing import image
import numpy as np
import requests
from pydantic import BaseModel, Field
from typing import Union



router = APIRouter()


@router.get("/")
def get_prediciton(
    image_path :Union[str, None] = Query(default="/home/ubuntu/winsport_pod_model/data/2/original_2_1.png", alias="image-path"),
):
    try:
        if not image_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Image path can't be empty"
            )


        raw_image = image.load_img(image_path, target_size=(224, 224))
        image_array = preprocess_input(
            np.expand_dims(image.img_to_array(raw_image), axis=0)
        )
        input_data = {
            "instances": image_array.tolist(),
        }
        data = json.dumps(input_data)
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
            detail=f"Internal Server Error due to {e}"
        )
