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
.. module:: U-net apply 1-axis
   :platform: Unix
   :synopsis: A plugin that takes in a reconstructed dataset\
   and returns a segmented dataset as output.

.. moduleauthor:: Olly King <olly.king@diamond.ac.uk>

"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin
from savu.test.test_utils import get_test_data_path
from pathlib import Path
from fastai.vision import Image, pil2tensor
from .unet_apply_helpers import (fix_odd_sides, create_model_from_zip,
                                 create_model_from_scratch)
import numpy as np
from skimage import img_as_float
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
        self.stats_obj.calc_stats = False
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        shape = in_dataset[0].get_shape()
        out_dataset[0].create_dataset(axis_labels=in_dataset[0],
                                          patterns=in_dataset[0],
                                          shape=shape, dtype = np.uint8)
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        # Store the precalculated mean and std dev 
        data = self.get_in_datasets()[0]
        self.data_mean = self.stats_obj.get_stats_from_dataset(data, 'mean')
        self.data_std_dev = self.stats_obj.get_stats_from_dataset(data, 'mean_std_dev')
        model_path = Path(self.parameters['model_file_path'])
        torch.cuda.set_device(self.parameters['GPU_index'])
        if self.parameters['testing']:
            test_path = get_test_data_path('unet_apply')
            self.model = create_model_from_scratch(test_path)
        else:
            self.model = create_model_from_zip(model_path)

    def process_frames(self, data):
        data = img_as_float(data[0])
        if self.parameters['clip_data']:
            # Clip the image
            std_dev_factor = self.parameters['std_dev_factor']
            lower_bound = self.data_mean - (self.data_std_dev * std_dev_factor)
            upper_bound = self.data_mean + (self.data_std_dev * std_dev_factor)
            if np.isnan(data).any():
                data = np.nan_to_num(data, copy=False, nan=self.data_mean)
            data = np.clip(data, lower_bound, upper_bound, out=data)
            data = np.subtract(data, lower_bound, out=data)
            data = np.divide(data, (upper_bound - lower_bound), out=data)
            data = np.clip(data, 0.0, 1.0, out=data)
        img = Image(pil2tensor(data, dtype=np.float32))
        flags = fix_odd_sides(img)
        prediction = self.model.predict(img)
        output_im = prediction[1][0]
        if 'y' in flags:
            ymax = list(output_im.shape)[0]
            output_im = output_im[:ymax-1, :]
        if 'x' in flags:
            xmax = list(output_im.shape)[1]
            output_im = output_im[:, :xmax-1]
        return output_im.cpu().numpy()

    def post_process(self):
        pass
