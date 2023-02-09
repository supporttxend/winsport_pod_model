from pathlib import Path
import json

import numpy as np
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image

try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)





def image_file_to_tensor(
    path="/home/ubuntu/winsport_pod_model/data/2/original_2_1.png",
):

    img = image.load_img(
        "/home/ubuntu/winsport_pod_model/data/2/original_2_1.png",
        target_size=(224, 224),
    )
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    input_data = {
        "instances": x.tolist(),
    }
    res = json.dumps(input_data)
    return res


headers = {"ContentType": "application/json"}
data = image_file_to_tensor()
from sagemaker.predictor import Predictor

endpoint_name = "pod-endpoint"
endpoint_name = "test-pod"

predictor = Predictor(endpoint_name=endpoint_name)

results = predictor.predict(data, initial_args=headers)

data = json.loads(results)


feature = data['predictions'][0]
# print(type(feature))
list_1 = feature
# print(list_1)
max_value = max(feature)
max_index = list_1.index(max_value)
print(max_index)
