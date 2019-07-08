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
.. module:: i23 beamline segmentation routine 
   :platform: Unix
   :synopsis: Wraps i23 segmentation code for Gaussian Mixture clustering   \
   and subsequent postprocessing of the segmented image

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
#from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.driver.multi_threaded_plugin import MultiThreadedPlugin
from savu.plugins.utils import register_plugin

import numpy as np
from sklearn.mixture import GaussianMixture
# i23 reconstruction and segmentation routines
from i23.methods.segmentation import MASK_CORR

@register_plugin
class I23Segment3d(Plugin, MultiThreadedPlugin):
    """
    A Plugin to segment reconstructed data from i23 beamline. The projection data \
    should be first reconstructed iteratively using the ToMoBAR plugin. The goal of \
    the segmentation plugin is to cluster and segment data using Gaussian Mixtures \
    and then apply iterative model-based segmentation to further process the obtained \
    mask. https://github.com/dkazanc/i23seg

    :param classes: The number of classes for GMM (take from 2D version). Default: 5.
    :param correction_window: The size of the correction (non-local) window. Default: 8.
    :param iterations: The number of iterations for segmentation. Default: 10.
    :param out_datasets: Default out dataset names. Default: ['maskGMM', 'maskGMM_proc']
    """

    def __init__(self):
        super(I23Segment3d, self).__init__("I23Segment3d")

    def setup(self):
    
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        out_dataset[1].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_3D', 'single')
        out_pData[0].plugin_data_setup('VOLUME_3D', 'single')
        out_pData[1].plugin_data_setup('VOLUME_3D', 'single')
        
    def pre_process(self):
        # extract given parameters
        self.classes = self.parameters['classes']
        self.iterationsNumb = self.parameters['iterations']
        self.CorrectionWindow = self.parameters['correction_window']
        
        # some fixed parameters
        if (self.classes == 4):
            self.class_names4 = ('crystal','air','loop') # classes to process (order matters)
            self.restricted_combinations_4classes = (('loop','crystal','liquor','loop'),
                                        ('air','loop','liquor','liquor'),
                                        ('air','loop','crystal','liquor'),
                                        ('air','crystal','loop','loop'),
                                        ('air','crystal','liquor','liquor'),
                                        ('air','liquor','loop','loop'))
        elif (self.classes == 5):
            self.class_names5 = ('liquor','air','loop') # classes to process (order matters)
            self.restricted_combinations_5classes = (('loop','crystal','liquor','loop'),
                                        ('air','artifacts','liquor','liquor'),
                                        ('air','loop','liquor','liquor'),
                                        ('air','artifacts','loop','loop'),
                                        ('air','crystal','loop','loop'),
                                        ('air','loop','crystal','crystal'))
        else:
            raise ("Choose 4 or 5 classes")

    def process_frames(self, data):
        # Do GMM classification/segmentation first
        dimensdata = data[0].ndim
        if (dimensdata == 2):
            (Nsize1, Nsize2) = np.shape(data[0])
            Nsize3 = 1
        if (dimensdata == 3):
            (Nsize1, Nsize2, Nsize3) = np.shape(data[0])
        
        #print(dimensdata)
        inputdata = data[0].reshape((Nsize1*Nsize2*Nsize3), 1)/np.max(data[0])
        
        if (self.classes == 4):
            classif = GaussianMixture(n_components=4, covariance_type="tied")
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
            # Post-processing part of obtained GMM masks (4 classes processing)
            pars4 = {'maskdata' : maskGMM,\
            'class_names': self.class_names4,\
            'total_classesNum': 4,\
            'restricted_combinations': self.restricted_combinations_4classes,\
            'CorrectionWindow' : self.CorrectionWindow ,\
            'iterationsNumb' : self.iterationsNumb}
            
            maskGMM_proc = MASK_CORR(pars4['maskdata'], pars4['class_names'], \
                    pars4['total_classesNum'], pars4['restricted_combinations'],\
                    pars4['CorrectionWindow'], pars4['iterationsNumb'])
        
        if (self.classes == 5):
            classif = GaussianMixture(n_components=5, covariance_type="tied")
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

            # 5 classes processing
            pars5 = {'maskdata' : maskGMM,\
            'class_names': self.class_names5,\
            'total_classesNum': 5,\
            'restricted_combinations': self.restricted_combinations_5classes,\
            'CorrectionWindow' : self.CorrectionWindow ,\
            'iterationsNumb' : self.iterationsNumb}
            
            maskGMM_proc = MASK_CORR(pars5['maskdata'], pars5['class_names'], \
                    pars5['total_classesNum'], pars5['restricted_combinations'],\
                    pars5['CorrectionWindow'], pars5['iterationsNumb'])
        
        return [maskGMM, maskGMM_proc]
    
    def nInput_datasets(self):
        return 1
    def nOutput_datasets(self):
        return 2