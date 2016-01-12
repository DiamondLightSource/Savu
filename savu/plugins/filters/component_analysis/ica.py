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
.. module:: simple_fit
   :platform: Unix
   :synopsis: A plugin to fit peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_component_analysis import BaseComponentAnalysis
from sklearn.decomposition import FastICA
import numpy as np


@register_plugin
class Ica(BaseComponentAnalysis):
    """
    This plugin performs independent component analysis on XRD/XRF spectra.
    """

    def __init__(self):
        super(Ica, self).__init__("ICA")

    def filter_frames(self, data):
        logging.debug("I am starting the old componenty vous")
        # data will already be shaped correctly
        if self.parameters['whiten']:
            data = data - np.mean(data)
        logging.debug("Making the matrix")
        ica = FastICA(n_components=self.parameters['number_of_components'])
        logging.debug("Performing the fit")
        S_ = ica.fit_transform(data)
        scores = np.reshape(S_, (self.images_shape))
        eigenspectra = ica.components_
        logging.debug("mange-tout")
        return [scores, eigenspectra]
