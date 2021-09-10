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
.. module:: dezinger_deprecated
   :platform: Unix
   :synopsis: A plugin to remove zingers

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import numpy as np
import dezing

from savu.plugins.filters.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin


class DezingerDeprecated(BaseFilter, CpuPlugin):

    def __init__(self):
        super(DezingerDeprecated, self).__init__("DezingerDeprecated")
        self.warnflag = 0
        self.errflag = 0

    def pre_process(self):
        # Apply dezing to dark and flat images
        inData = self.get_in_datasets()[0]
        dark = inData.data.dark()
        flat = inData.data.flat()
        self.data_size = inData.get_shape()

        pad_list = ((self.pad, self.pad), (0, 0), (0, 0))

        # dezing the dark field        print "*****in data shape in base filter", in_dataset[0].get_shape()

        if dark.size:
            (retval, self.warnflag, self.errflag) = dezing.setup_size(
                dark.shape, self.parameters['outlier_mu'], self.pad,
                mode=self.parameters['mode'])
            dark = self._dezing(np.pad(dark, pad_list, mode='edge'))
            inData.data.update_dark(dark[self.pad:-self.pad])
            (retval, self.warnflag, self.errflag) = dezing.cleanup()

        # dezing the flat field
        if flat.size:
            (retval, self.warnflag, self.errflag) = dezing.setup_size(
                flat.shape, self.parameters['outlier_mu'],
                self.pad, mode=self.parameters['mode'])
            flat = self._dezing(np.pad(flat, pad_list, mode='edge'))
            inData.data.update_flat(flat[self.pad:-self.pad])
            (retval, self.warnflag, self.errflag) = dezing.cleanup()

        # setup dezing for data
        self._dezing_setup(self.data_size)

    def _dezing_setup(self, shape):
        (retval, self.warnflag, self.errflag) = \
            dezing.setup_size(shape, self.parameters['outlier_mu'],
                              self.pad, mode=self.parameters['mode'])

    def _process_calibration_frames(self, data):
        nSlices = data.shape[self.proj_dim] - 2*self.pad
        nSublists = int(np.ceil(nSlices/float(self.frame_limit)))
        idx = np.array_split(np.arange(self.pad, nSlices+self.pad), nSublists)
        idx = [np.arange(a[0]-self.pad, a[-1]+self.pad+1) for a in idx]
        out_sl = np.tile([slice(None)]*3, [len(idx), 1])
        out_sl[:, self.proj_dim] = idx
        result = np.empty_like(data)
        for sl in out_sl:
            result[tuple(sl)] = self._dezing(data[tuple(sl)])
        return result

    def _dezing(self, data):
        result = np.empty_like(data)
        (retval, self.warnflag, self.errflag) = dezing.run(data, result)
        return result

    def process_frames(self, data):
        return self._dezing(data[0])

    def post_process(self):
        (retval, self.warnflag, self.errflag) = dezing.cleanup()

    def get_max_frames(self):
        return 'multiple'

    def raw_data(self):
        return True

    def set_filter_padding(self, in_data, out_data):
        in_data = in_data[0]
        self.pad = (self.parameters['kernel_size'] - 1) / 2
        in_data.padding = {'pad_multi_frames': self.pad}
        out_data[0].padding = {'pad_multi_frames': self.pad}

    def executive_summary(self):
        if self.errflag != 0:
            return(["ERRORS detected in dezing plugin, Check the detailed \
log messages."])
        if self.warnflag != 0:
            return(["WARNINGS detected in dezing plugin, Check the detailed \
log messages."])
        return ["Nothing to Report"]
