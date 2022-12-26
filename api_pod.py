from fastapi import APIRouter, UploadFile, File, Request, HTTPException, BackgroundTasks, status
from fastapi import APIRouter, Depends, HTTPException, status

import uvicorn
# from tensorflow.keras.preprocessing import image
# import numpy as np
# from keras.applications.vgg16 import VGG16, preprocess_input
# from keras.models import load_model
import shutil
from PIL import Image
import boto3
from pod_model.quries import upload_file_to_bucket, s3_auth, upload_file_to_bucket
from botocore.client import BaseClient
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/ping", status_code=200, description="***** Liveliness Check *****")
async def ping():
    return {"ping": "pong"}


def read_file(file):
    """method is used to read file and clean data for prediction

    Args:
        file (_type_): _description_

    Returns:
        _type_: _description_
    """
    f = open(file, "r")
    f = list(f)
    for i in range(len(f)):
        f[i] = f[i].replace("\n", "")
    return f


def get_class(feature, id):
    """method is used to predict class related to image

    Args:
        feature (_type_):passing array of classes

    Returns:
        _type_: return predicted class
    """
    list_1 = feature.tolist()
    list_1 = list_1[0]
    max_value = max(list_1)
    max_index = list_1.index(max_value)
    class_subset = read_file("class.txt")
    if id not in [int(i) for i in class_subset]:
        raise HTTPException(status_code=404, detail="User not exist")
    person_dict = {}
    for i in range(len(class_subset)):
        person_dict[class_subset[i]] = f"Person {class_subset[i]}"
    if int(class_subset[max_index]) != id:
        raise HTTPException(status_code=404, detail="Signature not match")
    return person_dict[class_subset[max_index]]


# @router.post("/{id}")
# async def image_prediction(id : int, request: Request, img: UploadFile = File(...)):
#     """endpoint used to return the class of image

#     Args:
#         img (UploadFile, optional): upload image file for prediction

#     Returns:
#         _type_: reaturn the class of the image
#     """
#     # For setting static url
#     client_host = request.client.host
#     client_host = f":/data/{img.filename}"
#     with open(f"data/{img.filename}", "wb") as buffer:
#         shutil.copyfileobj(img.file, buffer)
#     sized_image = image.load_img(f"data/{img.filename}", target_size=(224, 224))
#     saved_model = load_model("tl_model_v1.weights.best.hdf5")
#     im = Image.open(f"data/{img.filename}")
#     x = image.img_to_array(sized_image)
#     x.shape
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
#     feature = saved_model.predict(x)
#     predicted_class = get_class(feature, id)
#     data = {"Verified User ": f" {predicted_class}", "image": client_host}
#     return data


@router.post("/upload-signatures")
async def upload_sinature_files(user_id:str, signature: UploadFile = File(...), s3: BaseClient = Depends(s3_auth)):
    """This endpoint accepts a CSV file with a specific schema then uploads it to S3,
        converts it into a list of dictionaries and returns the list.

    Args:
        signature (UploadFile): CSV file with specific schema

    Returns:
        UploadCSVOut: list of dictionaries of contacts schema
    """

    # checking csv file type
    print(dir(signature), signature.file)
    if signature.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature file type is invalid.",
        )

    upload_obj = await upload_file_to_bucket(s3_client=s3, user_id=user_id, file_obj=signature.file,
                                       object_name=signature.filename
                                       )
    if upload_obj:
        return JSONResponse(content="Object has been uploaded to bucket successfully",
                            status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="File could not be uploaded")
