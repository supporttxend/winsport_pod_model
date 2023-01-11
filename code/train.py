import tensorflow as tf
from tensorflow.python.client import device_lib
import os

from keras.optimizers import Adam
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping

from pathlib import Path
import numpy as np
from livelossplot.inputs.keras import PlotLossesCallback
from models import create_model
from helper_funcitons import custom_functions as cf
import splitfolders
from config import settings
from quries import downlaod_data_set
import shutil
import datetime
import time
import pickle
import argparse
import traceback
import sys
import json
import codecs


try:
    BASE_DIR = Path(__file__).resolve().parent
    print("Try BASE", BASE_DIR)

except Exception as e:

    BASE_DIR = Path(".").parent.absolute()
    print("Except BASE", BASE_DIR)

RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
SM_MODEL_DIR = settings.SM_MODEL_DIR
SM_CHECK_POINT_DIR = settings.SM_CHECK_POINT_DIR

print("Script is running")

# print(device_lib.list_local_devices())

# try:
#     gpu = tf.config.experimental.list_physical_devices("GPU")
#     tf.config.experimental.set_memory_growth(gpu[0], True)
# except:
#     from tensorflow.compat.v1 import ConfigProto
#     from tensorflow.compat.v1 import InteractiveSession


#     def fix_gpu():
#         config = ConfigProto()
#         config.gpu_options.allow_growth = True
#         session = InteractiveSession(config=config)
#     fix_gpu()

def save_history(path, history):

    history_for_json = {}
    # transform float values that aren't json-serializable
    for key in list(history.history.keys()):
        if type(history.history[key]) == np.ndarray:
            history_for_json[key] == history.history[key].tolist()
        elif type(history.history[key]) == list:
            if (
                type(history.history[key][0]) == np.float32
                or type(history.history[key][0]) == np.float64
            ):
                history_for_json[key] = list(map(float, history.history[key]))

    with codecs.open(path, "w", encoding="utf-8") as f:
        json.dump(history_for_json, f, separators=(",", ":"), sort_keys=True, indent=4)

def save_model(model, output):

    # create a TensorFlow SavedModel for deployment to a SageMaker endpoint with TensorFlow Serving
    tf.keras.models.save_model(model, output+"/tensorflow_model/1")
    print("Model successfully saved at: {}".format(output))
    return

def main(args):

    try:

        BATCH_SIZE = args.batch_size
        EPOCH = args.epoch
        LEARNING_RATE = args.learning_rate


        input_path = BASE_DIR.parent / "input/data"
        # class_subset = sorted(os.listdir(BASE_PATH / DATA_SET_FOLDER / "train"))
        class_subset = sorted(os.listdir(os.path.join(input_path, "train")))

        train_generator = ImageDataGenerator(
            rotation_range=90,
            brightness_range=[0.1, 0.7],
            width_shift_range=0.5,
            height_shift_range=0.5,
            horizontal_flip=True,
            vertical_flip=True,
            validation_split=0.15,
            preprocessing_function=preprocess_input,
        )  # VGG16 preprocessing

        test_generator = ImageDataGenerator(preprocessing_function=preprocess_input)

        # download_dir = BASE_PATH / DATA_SET_FOLDER
        download_dir = input_path
        traingen, validgen, testgen = cf.image_generator(
            download_dir, train_generator, test_generator, class_subset, BATCH_SIZE
        )

        input_shape = (224, 224, 3)
        optim_1 = Adam(learning_rate=LEARNING_RATE)
        n_classes = len(class_subset)

        n_steps = traingen.samples // BATCH_SIZE
        n_val_steps = validgen.samples // BATCH_SIZE

        # First we'll train the model without Fine-tuning
        vgg_model = create_model(input_shape, n_classes, optim_1, fine_tune=2)
        vgg_model

        # plot_loss_1 = PlotLossesCallback()
        # print("plotloss :",plot_loss_1)
        # ModelCheckpoint callback - save best weights
        # tl_checkpoint_1 = ModelCheckpoint(
        #     filepath=args.output_data_dir "/ f"tl_model_v1_{int(time.time())}.weights.best.hdf6",
        #     save_best_only=True,
        #     monitor="accuracy",
        #     verbose=1,
        # )
        tl_checkpoint_1 = ModelCheckpoint(args.output_data_dir + "/checkpoint-{epoch}.h5")
        print("checkpoint", tl_checkpoint_1)

        Model_NAME = f"signature-model-{int(time.time())}"
        log_dir = f"logs/{Model_NAME}"
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

        vgg_history = vgg_model.fit(
            traingen,
            batch_size=BATCH_SIZE,
            epochs=EPOCH,
            validation_data=validgen,
            steps_per_epoch=n_steps,
            validation_steps=n_val_steps,
            callbacks=[tensorboard_callback, tl_checkpoint_1],
            verbose=1,
        )
        for key in vgg_history.history:
            print("For cehcking :", key)

        # with open(
        #     os.path.join(model_dir, f"pod-model-{int(time.time())}.pkl"), "wb"
        # ) as out:
        #     pickle.dump(vgg_model, out)
        print("Saving the model.")
        # save_history(model_dir + "/hvd_history.p", vgg_history)
        save_model(vgg_model, args.model_output_dir)

        print("Training complete.")

    except Exception as e:

        trc = traceback.format_exc()
        with open(os.path.join(args.output_dir, 'failure'), 'w') as s:
            s.write('Exception during training: ' + str(e) + '\n' + trc)

        print('Exception during training: ' + str(e) + '\n' + trc, file=sys.stderr)

        sys.exit(255)
if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-bs", "--batch_size", type=int, help="batch size", default=2)
    argParser.add_argument("-e", "--epoch", type=int, help="epoch size", default=3)
    argParser.add_argument("-lr", "--learning_rate", type=float, help="learning rate", default=0.001)
    argParser.add_argument("--tensorboard-dir", type=str, default=os.environ.get("SM_MODULE_DIR"))
    argParser.add_argument("--model_output_dir", type=str, help="model dir", default=os.environ.get("SM_MODEL_DIR"))
    argParser.add_argument("--output_data_dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR"))
    argParser.add_argument("--output_dir", type=str, help="model dir", default=os.environ.get("SM_OUTPUT_DIR"))

    args = argParser.parse_args()
    print("ARGS ------------>", args)

    # print("args.name=", args.name)
    main(args)
