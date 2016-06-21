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
# $Id: dezing_filter.py 467 2016-02-16 11:40:42Z kny48981 $


"""
.. module:: dezing_filter
   :platform: Unix
   :synopsis: A plugin to remove dezingers

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import dezing

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class DezingFilter(BaseFilter, CpuPlugin):
    """
    A plugin for cleaning x-ray strikes based on statistical evaluation of \
    the near neighbourhood
    :param outlier_mu: Threshold for detecting outliers, greater is less \
    sensitive. Default: 10.0.
    :param kernel_size: Number of frames included in average. Default: 5.
    """

    def __init__(self):
        super(DezingFilter, self).__init__("DezingFilter")
        self.warnflag = 0
        self.errflag = 0

    def pre_process(self):
        # Apply dezing to dark and flat images (data with image key only)
        inData = self.get_in_datasets()[0]
        dark = inData.data.dark()
        flat = inData.data.flat()
        (retval, self.warnflag, self.errflag) = \
            dezing.setup_size(dark.shape, self.parameters['outlier_mu'], 0)
        inData.meta_data.set_meta_data('dark', self._dezing(dark).mean(0))
        inData.meta_data.set_meta_data('flat', self._dezing(flat).mean(0))
        (retval, self.warnflag, self.errflag) = dezing.cleanup()

        # setup dezing for data
        (retval, self.warnflag, self.errflag) = \
            dezing.setup_size(self.data_size, self.parameters['outlier_mu'],
                              self.pad)

    def _dezing(self, data):
        result = np.empty_like(data)
        (retval, self.warnflag, self.errflag) = dezing.run(data, result)
        return result

    def filter_frames(self, data):
        return self._dezing(data[0])

    def post_process(self):
        (retval, self.warnflag, self.errflag) = dezing.cleanup()

    def get_max_frames(self):
        """
        :returns:  an integer of the number of frames. Default 100
        """
        return 16

#    def set_filter_padding(self, in_data, out_data):
#        in_data = in_data[0]
#        self.pad = (self.parameters['kernel_size'] - 1) / 2
#        self.data_size = in_data.get_shape()
#        in_data.padding = {'pad_multi_frames': self.pad}
#        out_data[0].padding = {'pad_multi_frames': self.pad}

    def set_filter_padding(self, in_data, out_data):
        in_data = in_data[0]
        self.pad = 0
#        self.pad = (self.parameters['kernel_size'] - 1) / 2
        self.data_size = in_data.get_shape()
#        in_data.padding = {'pad_frame_edges': self.pad}
#        out_data[0].padding = {'pad_frame_edges': self.pad}

#    def get_plugin_pattern(self):
#        return 'SINOGRAM'
#
#    def fix_data(self):
#        return True

    def executive_summary(self):
        if self.errflag != 0:
            return(["ERRORS detected in dezing plugin, Check the detailed \
log messages."])
        if self.warnflag != 0:
            return(["WARNINGS detected in dezing plugin, Check the detailed \
log messages."])
        return "Nothing to Report"
