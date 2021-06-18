# Copyright 2019 Diamond Light Source Ltd.
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
.. module:: gmm_segment3d
   :platform: Unix
   :synopsis: Gaussian mixture models for classification-segmentation routine. Wrapper around scikit GMM function

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from sklearn.mixture import GaussianMixture

@register_plugin
class GmmSegment3d(Plugin, MultiThreadedPlugin):

    def __init__(self):
        super(GmmSegment3d, self).__init__("GmmSegment3d")

    def setup(self):

        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0], dtype=np.uint8)
        in_pData, out_pData = self.get_plugin_datasets()

        getall = ["VOLUME_XZ", "voxel_y"]
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single', getall=getall)

    def pre_process(self):
        # extract given parameters
        self.classes = self.parameters['classes']

    def process_frames(self, data):
        # Do GMM classification/segmentation first
        dimensdata = data[0].ndim
        if (dimensdata == 2):
            (Nsize1, Nsize2) = np.shape(data[0])
            Nsize3 = 1
        if (dimensdata == 3):
            (Nsize1, Nsize2, Nsize3) = np.shape(data[0])

        inputdata = data[0].reshape((Nsize1*Nsize2*Nsize3), 1)/np.max(data[0])

        #run classification and segmentation
        classif = GaussianMixture(n_components=self.classes, covariance_type="tied")
        classif.fit(inputdata)
        cluster = classif.predict(inputdata)
        segm = classif.means_[cluster]
        if (dimensdata == 2):
            segm = segm.reshape(Nsize1, Nsize3, Nsize2)
        else:
            segm = segm.reshape(Nsize1, Nsize2, Nsize3)
        maskGMM = segm.astype(np.float64) / np.max(segm)
        maskGMM = 255 * maskGMM # Now scale by 255
        maskGMM = maskGMM.astype(np.uint8) # obtain the GMM mask
        return [maskGMM]

    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 1
