from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from helper_funcitons.custom_functions import load_model, get_path
from pathlib import Path
from tensorflow.keras.preprocessing import image
import numpy as np


try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

model_dir_path = BASE_DIR.parent / "model"
model = load_model(model_dir_path)

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import io

def image_file_to_tensor(path="/home/ubuntu/winsport_pod_model/data/2/original_2_1.png"):

    img = image.load_img("/home/ubuntu/winsport_pod_model/data/2/original_2_1.png", target_size=(224,224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    input_data = {
        'instances': x.tolist(),
        }
    res = json.dumps(input_data)
    return res
headers = {"Content-Type": "application/json"}
data = image_file_to_tensor()
json_response = requests.post("http://localhost:8080/invocations", data=data, headers=headers)






feature = json_response.json()['predictions']
print(type(feature))
list_1 = feature
list_1 = list_1[0]
print(list_1)
max_value = max(list_1)
max_index = list_1.index(max_value)
print(max_index)