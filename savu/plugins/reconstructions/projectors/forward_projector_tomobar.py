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
.. module:: forward_projector_tomobar
   :platform: Unix
   :synopsis: A forward data projector using ToMoBAR software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from tomobar.methodsDIR import RecToolsDIR
import numpy as np

@register_plugin
class ForwardProjectorTomobar(BaseRecon, CpuPlugin):
    """
    This plugin uses ToMoBAR software and CPU Astra projector to generate projection data,
    one needs to provide 2 inputs [original projection data, object to project].
    The plugin will project the given object using geometry of the provided projection data

    :param out_datasets: Default out dataset names. Default: ['forw_proj']
    """

    def __init__(self):
        super(ForwardProjectorTomobar, self).__init__('ForwardProjectorTomobar')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames())
        in_pData[1].plugin_data_setup('VOLUME_XZ', 'single')

        out_shape_sino = in_dataset[0].get_shape()
        out_dataset[0].create_dataset(patterns=in_dataset[0],
                                           axis_labels=in_dataset[0],
                                           shape=out_shape_sino)
        out_pData[0].plugin_data_setup('SINOGRAM',self.get_max_frames())

    def process_frames(self, data):
        cor, angles, vol_shape, init  = self.get_frame_params()
        sinogram = data[0].astype(np.float32)
        image = data[1].astype(np.float32)
        objsize_image = np.shape(image)[0]
        proj_number, self.DetectorsDimH = np.shape(sinogram)
        self.anglesRAD = np.deg2rad(angles.astype(np.float32))
        half_det_width = 0.5*self.DetectorsDimH
        cor_astra = half_det_width - cor
        RectoolsDIR = RecToolsDIR(DetectorsDimH = self.DetectorsDimH+1,  # DetectorsDimH # detector dimension (horizontal)
                            DetectorsDimV = None,  # DetectorsDimV # detector dimension (vertical) for 3D case only
                            CenterRotOffset = cor_astra.item() - 0.5, # Center of Rotation (CoR) scalar (for 3D case only)
                            AnglesVec = self.anglesRAD, # array of angles in radians
                            ObjSize = objsize_image, # a scalar to define reconstructed object dimensions
                            device_projector='cpu')
        sinogram_new = RectoolsDIR.FORWPROJ(image)
        return sinogram_new

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 2

    def nOutput_datasets(self):
        return 1
