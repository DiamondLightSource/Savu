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
.. module:: xrf_saver
   :platform: Unix
   :synopsis: A class to save output in tiff format

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from mpi4py import MPI
import os
import numpy as np
from savu.plugins.savers.base_saver import BaseSaver
from savu.plugins.utils import register_plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from fabio.edfimage import EdfImage
import collections


@register_plugin
class XrfSaver(BaseSaver, CpuPlugin):
    def __init__(self, name='XrfSaver'):
        super(XrfSaver, self).__init__(name)
        self.folder = None
        self.data_name = None
        self.file_name = None
        self.group_name = None

    def pre_process(self):
        self.data_name = self.get_in_datasets()[0].get_name()
        self.group_name = self._get_group_name(self.data_name)
        self.folder = "%s/%s-%s" % (self.exp.meta_data.get("out_path"),
                                    self.name, self.data_name)
        if MPI.COMM_WORLD.rank == 0:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
        in_pData, __out_pData = self.get_plugin_datasets()
        in_datasets, __out_datasets = self.get_datasets()
        self.axis_labels = in_datasets[0].get_axis_labels()
        sd = in_datasets[0].get_slice_dimensions()
        self.axes = [self.axis_labels[ix] for ix in sd]
        self.axis_info = []
        k = 0
        for ix in self.axes:
            axis_name = list(ix.keys())[0]
            try:
                foo = in_datasets[0].meta_data.get(axis_name)# take the first key
            except KeyError:
                foo = np.array(list(range(in_datasets[0].get_shape()[sd[k]]))) # if it doesn't exis then replace it with a range
            k+=1
            self.axis_info.append(foo)
        #self.axis_info = [in_datasets[0].meta_data.get(ix) for ix in self.axes]

    def process_frames(self, data):
        d=data[0] # first dataset in the list
        print("################################")
        print("number of datasets in list",len(data))
        print("shape of data[0]", data[0].shape)
        print("################################")
#         frame = self.get_current_slice_list()[0] # slice list for the first dataset
#         frame = [ix.start for ix in frame] #  convert to just numbers
#         channel = self.axis_info[0][frame[-2]]
#         elements = self.axis_info[1][frame[-1]]
#         foo = data[0]
#         header = collections.OrderedDict()     
#         header['HeaderID'] = 'EH:000001:000000:000000'
#         header['Image'] = '1'
#         header['ByteOrder'] = 'LowByteFirst'
#         header['DataType']=  'DoubleValue'
#         header['Dim_1'] = str(foo.shape[-1]) 
#         header['Dim 2'] = str(foo.shape[-2])
#         header['Size'] = str(8.0*np.prod(foo.shape))
#         out_title = "%s_channel_%s" % (elements.replace(" ","_"), str(channel))
#         header['Title'] = out_title
#         fout = EdfImage(foo, header)
#         filename = self.folder+os.sep + str(out_title) + '.edf'
#         fout.write(filename)

    def get_pattern(self):
        return "PROJECTION"


    def get_max_frames(self):
        in_datasets, __out_datasets = self.get_datasets()
        sh = in_datasets[0].get_shape()
        print("full dataset shape:",sh)
        nframes = np.prod(sh[-2:])# product of the channel and the number of elements in the fit
        print("max frames requested:",nframes, type(nframes))
        return nframes