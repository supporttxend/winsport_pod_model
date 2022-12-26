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


RAW_DATA_FOLDER = settings.RAW_DATA_FOLDER
DATA_SET_FOLDER = settings.DATA_SET_FOLDER
BASE_PATH = Path("")
BATCH_SIZE = 2

# print(device_lib.list_local_devices())

try:
    gpu = tf.config.experimental.list_physical_devices("GPU")
    tf.config.experimental.set_memory_growth(gpu[0], True)
except:
    from tensorflow.compat.v1 import ConfigProto
    from tensorflow.compat.v1 import InteractiveSession


    def fix_gpu():
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        session = InteractiveSession(config=config)


    fix_gpu()

def main():

    # try:
    #     resp = downlaod_data_set()
    #     if not resp:
    #         print("error at downloading files")
    #     else:
    #         if os.path.exists(DATA_SET_FOLDER):
    #             shutil.rmtree(DATA_SET_FOLDER, ignore_errors=True)

    #         splitfolders.ratio(
    #             RAW_DATA_FOLDER,
    #             output=DATA_SET_FOLDER,
    #             seed=0,
    #             ratio=(0.8, 0, 0.2),
    #             group_prefix=None,
    #             move=False,
    #         )

    # except Exception as e:
    #     print(f"Error at downloading and spliting images, {e}")


    class_subset = sorted(os.listdir(BASE_PATH / DATA_SET_FOLDER / "train"))

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

    download_dir = BASE_PATH / DATA_SET_FOLDER
    traingen, validgen, testgen = cf.image_generator(
        download_dir, train_generator, test_generator, class_subset, BATCH_SIZE
    )


    input_shape = (224, 224, 3)
    optim_1 = Adam(learning_rate=0.001)
    n_classes = len(class_subset)

    n_steps = traingen.samples // BATCH_SIZE
    n_val_steps = validgen.samples // BATCH_SIZE
    n_epochs = 2000

    # First we'll train the model without Fine-tuning
    vgg_model = create_model(input_shape, n_classes, optim_1, fine_tune=2)
    vgg_model


    # plot_loss_1 = PlotLossesCallback()
    # print("plotloss :",plot_loss_1)
    # ModelCheckpoint callback - save best weights
    tl_checkpoint_1 = ModelCheckpoint(
        filepath="tl_model_v1.weights.best.hdf6",
        save_best_only=True,
        monitor="accuracy",
        verbose=1,
    )
    print("checkpoint", tl_checkpoint_1)

    Model_NAME = (
        f"signature-model-{int(time.time())}"
    )
    log_dir = f"logs/{Model_NAME}"
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

    vgg_history = vgg_model.fit(
        traingen,
        batch_size=BATCH_SIZE,
        epochs=n_epochs,
        validation_data=validgen,
        steps_per_epoch=n_steps,
        validation_steps=n_val_steps,
        callbacks=[tensorboard_callback, tl_checkpoint_1],
        verbose=1,
    )
    for key in vgg_history.history:
        print("For cehcking :", key)

    # with open(os.path.join(model_path, 'pod-model.pkl'), 'wb') as out:
    #     pickle.dump(vgg_model, out)
    # print('Training complete.')


if __name__ == "__main__":
    main()
