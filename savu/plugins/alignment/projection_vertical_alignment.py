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
.. module:: projection_vertical_alignment
   :platform: Unix
   :synopsis: Align each projection vertically with shift values calculated\
       using the ProjectionShift plugin

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import numpy as np
from scipy.ndimage.interpolation import shift as sci_shift

from savu.plugins.utils import register_plugin
from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin


@register_plugin
class ProjectionVerticalAlignment(BaseFilter, CpuPlugin):

    def __init__(self):
        logging.debug("initialising Sinogram Alignment")
        super(ProjectionVerticalAlignment, self).__init__(
            "ProjectionVerticalAlignment")

    def pre_process(self):
        data = self.get_in_datasets()[0]
        self.shift = data.meta_data.get('proj_align_shift')
        self.slice_dir = data._get_plugin_data().get_slice_dimension()
        self.sl = [slice(None)]*3
        self.det_y = self.get_plugin_in_datasets()[0].\
            get_data_dimension_by_axis_label('detector_y')

    def process_frames(self, data):
        data = data[0]
        output = np.empty_like(data)
        nFrames = data.shape[self.slice_dir]
        sl = self.slice_list[self.slice_dir]
        entries = np.arange(sl.start, sl.stop, sl.step)

        for i in range(nFrames):
            self.sl[self.slice_dir] = i
            output[self.sl] = \
                sci_shift(data[self.sl], (self.shift[entries[i]][0], 0), cval=np.nan)

        return output
