# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: plugin_template1
   :platform: Unix
   :synopsis: A template to create a simple plugin that takes one dataset as\
   input and returns a similar dataset as output.

.. moduleauthor:: Developer Name <email@address.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin
from pathlib import Path
from fastai.vision import open_image, Image, pil2tensor
from .unet_apply_helpers import fix_odd_sides, create_model_from_zip
import numpy as np
from skimage import io, img_as_ubyte, img_as_float
from zipfile import ZipFile
import os
import json
import torch


@register_plugin
class UnetApply(Plugin, GpuPlugin):

    def __init__(self):
        super(UnetApply, self).__init__('UnetApply')

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        # AMEND THE PATTERNS: The output dataset will have one dimension more
        # than the in_dataset, so add another slice dimensions the patterns
        add_dim = str(len(in_dataset[0].get_shape()))
        patterns = {in_dataset[0]: ['.'.join(['*', add_dim])]}

        # AMEND THE AXIS LABELS: Add an extra slice dim to all axis labels
        axis_list = ['.'.join(['~' + add_dim, 'label',
                            'probability'])]
        axis_labels = {in_dataset[0]: axis_list}

        # AMEND THE SHAPE: Remove the two unrequired dimensions from the
        # original shape and add a new dimension shape.
        self.rep = self.parameters['number_of_labels']
        shape = list(in_dataset[0].get_shape())
        shape.append(self.rep)

        # populate the output dataset
        out_dataset[0].create_dataset(
                patterns=patterns,
                axis_labels=axis_labels,
                shape=tuple(shape))

        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], self.rep,
                                       slice_axis='label')

    def pre_process(self):
        model_path = Path(self.parameters['model_file_path'])
        torch.cuda.set_device(self.parameters['GPU_index'])
        self.model = create_model_from_zip(model_path)

    def process_frames(self, data):
        # do some processing here
        # here is how to access a parameter defined in the tools file
        data = img_as_float(data[0])
        prediction = self.predict_single_image(data)
        if self.parameters['rotate_images']:
            for k in range(1, 4):
                data = np.rot90(data, 1)
                rotated_pred = self.predict_single_image(np.ascontiguousarray(data))
                unrotated_pred = torch.rot90(rotated_pred, -k)
                prediction = torch.max(prediction, unrotated_pred)
        return prediction

    def predict_single_image(self, data):
        img = Image(pil2tensor(data, dtype=np.float32))
        flags = fix_odd_sides(img)
        prediction = self.model.predict(img)[2]
        prediction = self.revert_image_dimensions(flags, prediction)
        return self.transpose_data(prediction)

    def transpose_data(self, prediction):
        prediction = torch.transpose(prediction, 0, 2)
        if self.parameters['pattern'] in ['VOLUME_YZ', 'VOLUME_XY']:
            prediction = torch.transpose(prediction, 1, 0)
        else:
            prediction = torch.transpose(prediction, 0, 1)
        return prediction

    def revert_image_dimensions(self, flags, prediction):
        if 'y' in flags:
            ymax = list(prediction.shape)[1]
            prediction = prediction[:, :ymax-1, :]
        if 'x' in flags:
            xmax = list(prediction.shape)[2]
            prediction = prediction[:, :, :xmax-1]
        return prediction

    def post_process(self):
        pass
    