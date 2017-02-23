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
.. module:: nxstxm_loader
   :platform: Unix
   :synopsis: A class for loading nxstxm data

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

from savu.plugins.loaders.base_loader import BaseLoader
import numpy as np
from savu.plugins.utils import register_plugin
import logging
import h5py


@register_plugin
class I13FluoLoader(BaseLoader):
    """
    A class to load tomography data from an NXstxm file
    :param fluo_offset: fluo scale offset. Default: 0.0.
    :param fluo_gain: fluo gain. Default: 0.01.
    """

    def __init__(self, name='I13FluoLoader'):
        super(I13FluoLoader, self).__init__(name)

    def setup(self):
        """
         Define the input nexus file

        :param path: The full path of the NeXus file to load.
        :type path: str
        """

        data_str = 'entry1/xmapMca/fullSpectrum'
        exp = self.exp
        data_obj = exp.create_data_object("in_data", 'fluo')
        data_obj.backing_file = \
            h5py.File(exp.meta_data.get("data_file"), 'r')
        data_obj.data = data_obj.backing_file[data_str]
        data_obj.set_shape(data_obj.data.shape)
        npts = data_obj.data.shape[-1]
        gain = self.parameters["fluo_gain"]
        energy = np.arange(self.parameters["fluo_offset"], gain*npts, gain)
        data_obj.meta_data.set("energy", energy)
        labels = []
        ### set the x
        x = \
            data_obj.backing_file['entry1/xmapMca/t1_sx'].value
        data_obj.meta_data.set('x', x)
        # axis label
        
        ### set the y
        y = \
            data_obj.backing_file['entry1/xmapMca/t1_sy'].value
        pos = np.zeros((2,len(y)))
        pos[0,:] = x
        pos[1,:] = y
        data_obj.meta_data.set('xy', pos)
        # axis label
        labels.append('xy.microns')
        labels.append('idx.idx')
#         labels.append('y.microns')
        # now set them
        labels.extend(['spectra.counts'])
#         print "the labels are:"+str(labels)
        data_obj.set_axis_labels(*tuple(labels))

        
        dims = range(len(data_obj.get_shape()))
        spec_core = (-1,) # it will always be this
#         print spec_core
        
        spec_slice = tuple(dims[:-1])
#         print spec_slice
        logging.debug("is a spectrum")
        logging.debug("the spectrum cores are:"+str(spec_core))
        logging.debug("the spectrum slices are:"+str(spec_slice))
        data_obj.add_pattern("SPECTRUM", core_dir=spec_core,
                             slice_dir=spec_slice)
        data_obj.add_pattern("SINOGRAM", core_dir=(0,1),
                     slice_dir=(2,))
        data_obj.add_pattern("PROJECTION", core_dir=(0,),
                     slice_dir=(1,2))
        self.set_data_reduction_params(data_obj)
