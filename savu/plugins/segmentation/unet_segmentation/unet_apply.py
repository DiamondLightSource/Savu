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
from pathlib import Path
from fastai.vision import Image, pil2tensor
from .unet_apply_helpers import fix_odd_sides, create_model_from_zip
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
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')
        out_pData[0].plugin_data_setup(self.parameters['pattern'], 'single')

    def pre_process(self):
        model_path = Path(self.parameters['model_file_path'])
        torch.cuda.set_device(self.parameters['GPU_index'])
        self.model = create_model_from_zip(model_path)

    def process_frames(self, data):
        # do some processing here
        # here is how to access a parameter defined in the tools file
        data = img_as_float(data[0])
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
        return output_im

    def post_process(self):
        pass