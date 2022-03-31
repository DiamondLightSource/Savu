import json
import os
from pathlib import Path
import numpy as np
from zipfile import ZipFile
from fastai.vision import (SegmentationItemList, get_transforms,
                           imagenet_stats, models, crop_pad, unet_learner)
from skimage import io, img_as_ubyte


def fix_odd_sides(image):
        """Replaces an an odd image dimension with an even dimension by padding.
    
        Taken from https://forums.fast.ai/t/segmentation-mask-prediction-on-different-input-image-sizes/44389/7.

        Args:
            image (fastai.vision.Image): The image to be fixed.
        """
        flags = []
        image_size = list(image.size)
        if (image_size[0] % 2) != 0:
            image = crop_pad(image,
                            size=(image_size[0]+1,
                            image_size[1]),
                            padding_mode='reflection')
            flags.append('y')

        if (image_size[1] % 2) != 0:
            image = crop_pad(image,
                            size=(image_size[0],
                            image_size[1] + 1),
                            padding_mode='reflection')
            flags.append('x')
        return flags

def create_dummy_data_files(dummy_dir):
    """Creates dummy data files on disk.

    Args:
        dummy_dir (pathlib.Path): Path to the directory in which to create files.
    """
    dummy_fns = ['data_z_stack_0.png', 'seg_z_stack_0.png']
    os.makedirs(dummy_dir, exist_ok=True)
    for fn in dummy_fns:
        dummy_im = np.random.randint(256, size=(256, 256), dtype=np.uint8)
        io.imsave(dummy_dir/fn, img_as_ubyte(dummy_im))
    
def create_dummy_dataset(dummy_dir, codes):
    """Creates a fastai segmentation dataset."""
    get_y_fn = lambda x: dummy_dir/f'{"seg" + x.stem[4:]}{x.suffix}'
    src = (SegmentationItemList.from_folder(dummy_dir)
                    .split_none()
                    .label_from_func(get_y_fn, classes=codes))
    data = (src.transform(get_transforms(), size=256, tfm_y=True)
                    .databunch(no_check=True)
                    .normalize(imagenet_stats))
    return data


def create_model_from_zip(model_filepath):
    """Creates a fastai unet_learner model from a zipfile.

    Args:
        model_filepath (pathlib.Path): Path to the zip file containing model
        weights and a JSON file containing label codes.

    Returns:
        fastai.vision.models.unet_learner: A U-Net model with the weights loaded.
    """
    root_dir = model_filepath.parent
    dummy_dir = root_dir/'dummy_imgs'
    create_dummy_data_files(dummy_dir)
    output_dir = root_dir/"extracted_model_files"
    os.makedirs(output_dir, exist_ok=True)
    with ZipFile(model_filepath, mode='r') as zf:
        zf.extractall(output_dir)
    with open(output_dir/f"{model_filepath.stem}_codes.json") as jf:
        codes = json.load(jf)
    # Convert codes to list if currently dict (e.g. from SuRVoS2)
    if isinstance(codes, dict):
        codes = [f"label_val_{i}" for i in codes]
    data = create_dummy_dataset(dummy_dir, codes)
    model = unet_learner(data, models.resnet34, model_dir=output_dir)
    model.load(model_filepath.stem)
    # Remove the restriction on the model prediction size
    model.data.single_ds.tfmargs['size'] = None
    return model

def create_model_from_scratch(test_path):
    """Creates a fastai unet_learner model from scratch

    Returns:
        fastai.vision.models.unet_learner: A U-Net model.
    """
    dummy_dir = Path(test_path, 'dummy_imgs')
    create_dummy_data_files(dummy_dir)
    codes = [f"label_val_{i}" for i in range(3)]
    data = create_dummy_dataset(dummy_dir, codes)
    model = unet_learner(data, models.resnet34)
    # Remove the restriction on the model prediction size
    model.data.single_ds.tfmargs['size'] = None
    return model
    