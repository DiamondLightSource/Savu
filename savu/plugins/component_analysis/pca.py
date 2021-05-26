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
.. module:: pca
   :platform: Unix
   :synopsis: A plugin to fit peaks

.. moduleauthor:: Aaron Parsons <scientificsoftware@diamond.ac.uk>

"""
import logging
from savu.plugins.utils import register_plugin
from savu.plugins.component_analysis.base_component_analysis \
    import BaseComponentAnalysis
from sklearn.decomposition import PCA
import numpy as np


@register_plugin
class Pca(BaseComponentAnalysis):

    def __init__(self):
        super(Pca, self).__init__("Pca")

    def process_frames(self, data):
        logging.debug("Starting the PCA")
        data = data[0]
        sh = data.shape
        newshape = (np.prod(sh[:-1]), sh[-1])
        data = np.reshape(data, (newshape))
        # data will already be shaped correctly
        logging.debug("Making the matrix")
        pca = PCA(n_components=self.parameters['number_of_components'],
                      whiten=self.parameters['whiten'])
        logging.debug("Performing the fit")
        data = self.remove_nan_inf(data)  #otherwise the fit flags up an error for obvious reasons
#         print "I'm here"
        S_ = pca.fit_transform(data)

#         print "S_Shape is:"+str(S_.shape)
#         print "self.images_shape:"+str(self.images_shape)
        loading = np.reshape(S_, (self.images_shape))
        scores = pca.components_
        logging.debug("mange-tout")
        return [loading, scores]
