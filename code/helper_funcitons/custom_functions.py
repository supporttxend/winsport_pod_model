import glob
import os
import pickle
import tarfile

PATHS = {
    "hyperparameters": "input/config/hyperparameters.json",
    "input": "input/config/inputdataconfig.json",
    "data": "input/data/",
    "model": "model/",
}


def image_generator(
    download_dir, train_generator, test_generator, class_subset, BATCH_SIZE
):

    # train_data_dir = download_dir / "train"
    # # val_data_dir = download_dir / "/val"
    # test_data_dir = download_dir / "test"

    train_data_dir = os.path.join(download_dir, "train")
    # val_data_dir = os.path.join(download_dir, "/val)"
    test_data_dir = os.path.join(download_dir, "test")

    traingen = train_generator.flow_from_directory(
        train_data_dir,
        target_size=(224, 224),
        class_mode="categorical",
        classes=class_subset,
        subset="training",
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=42,
    )

    validgen = train_generator.flow_from_directory(
        train_data_dir,
        target_size=(224, 224),
        class_mode="categorical",
        classes=class_subset,
        subset="validation",
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=42,
    )

    testgen = test_generator.flow_from_directory(
        test_data_dir,
        target_size=(224, 224),
        class_mode=None,
        classes=class_subset,
        batch_size=1,
        shuffle=False,
        seed=42,
    )

    return traingen, validgen, testgen


def get_path(key):
    return "/opt/ml/" + PATHS[key]


def load_model(model_dir_path):
    model_file = None
    filelist = glob.glob(str(model_dir_path / "pod-model-*.pkl"))
    model_path = str(model_dir_path / "model.tar.gz")
    model_pkl_path = glob.glob(str(model_dir_path / "pod-model-*.pkl"))
    if not filelist:
        with tarfile.open(model_path) as tar:
            tar.extractall(path=".")

    with open(model_pkl_path[0], "rb") as out:
        model_file = pickle.load(out)

    return model_file
