import os

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
