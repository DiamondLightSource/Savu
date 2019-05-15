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
.. module:: i23 beamline segmentation routine (apply after ToMoBAR reconstruction plugin)
   :platform: Unix
   :synopsis: Wraps i23 segmentation code for Gaussian Mixture clustering   \
   and subsequent postprocessing of the segmented image

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.reconstructions.base_recon import BaseRecon
#from savu.data.plugin_list import CitationInformation
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

import numpy as np
# i23 reconstruction and segmentation routines
# https://github.com/dkazanc/i23seg
# from i23.methods.segmentation import MASK_CORR
from sklearn.mixture import GaussianMixture

@register_plugin
class I23Segment(BaseRecon, CpuPlugin):
    """
    A Plugin to segment reconstructed data from i23 beamline. The projection data \
    should be first reconstructed iteratively using ToMoBAR plugin. The goal of \
    the segmentation plugin is to cluster and segment data using Gaussian Mixtures \
    and then apply iterative model-based segmentation to further process the obtained \
    mask.    

    :param correction_window: The size of the correction window. Default: 10.
    :param iterations: The number of iterations for segmentation. Default: 20.
    """

    def __init__(self):
        super(I23Segment, self).__init__("I23Segment")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
        out_pData[0].plugin_data_setup('VOLUME_XZ', 'single')
    
    def pre_process(self):
        # extract given parameters
        self.iterationsNumb = self.parameters['iterations']
        self.CorrectionWindow = self.parameters['correction_window']       

	# some fixed parameters
        self.class_names = ('crystal','air','loop') # classes to process (order matters)
        self.restricted_combinations_5classes = (('loop','crystal','liquor','loop'),
                                    ('air','artifacts','liquor','liquor'),
                                    ('air','loop','liquor','liquor'),
                                    ('air','artifacts','loop','loop'),
                                    ('air','crystal','loop','loop'),
                                    ('air','loop','crystal','crystal'))
        self.restricted_combinations_4classes = (('loop','crystal','liquor','loop'),
                                    ('air','loop','liquor','liquor'),
                                    ('air','loop','crystal','liquor'),
                                    ('air','crystal','loop','loop'),
                                    ('air','crystal','liquor','liquor'),
                                    ('air','liquor','loop','loop'))

    def process_frames(self, data):
        # Do GMM classification/segmentation first
        dimensdata = data[0].ndim
        if (dimensdata == 2):
            (Nsize1, Nsize2) = np.shape(data[0])
            Nsize3 = 1
        if (dimensdata == 3):
            (Nsize1, Nsize2, Nsize3) = np.shape(data[0])
        
        inputdata = data[0].reshape((Nsize1*Nsize2*Nsize3)**dimensdata, 1)/np.max(data[0])
        
        classes_number = 5
        classif = GaussianMixture(n_components=classes_number, covariance_type="tied")
        classif.fit(inputdata)
        cluster = classif.predict(inputdata)
        segm = classif.means_[cluster]
        segm = segm.reshape(Nsize1, Nsize2, Nsize3)
        maskGMM5 = segm.astype(np.float64) / np.max(segm)
        maskGMM5 = 255 * maskGMM5 # Now scale by 255
        maskGMM5 = maskGMM5.astype(np.uint8) # obtain the GMM mask

        classes_number = 4
        classif = GaussianMixture(n_components=classes_number, covariance_type="tied")
        classif.fit(inputdata)
        cluster = classif.predict(inputdata)
        segm = classif.means_[cluster]
        segm = segm.reshape(Nsize1, Nsize2, Nsize3)
        maskGMM4 = segm.astype(np.float64) / np.max(segm)
        maskGMM4 = 255 * maskGMM4 # Now scale by 255
        maskGMM4 = maskGMM4.astype(np.uint8) # obtain the GMM mask
        #pars['maskdata'] = np.nan_to_num(data[0])
        
        # Post-processing part of GMM masks
        
        return [maskGMM4,maskGMM5]
    
    def nOutput_datasets(self):
        return 2
    def get_max_frames(self):
        return 'single'
   
