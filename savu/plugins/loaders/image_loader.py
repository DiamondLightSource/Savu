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
.. module:: image_loader
   :platform: Unix
   :synopsis: A class for loading fits data.

.. moduleauthor:: Srikanth Nagella <scientificsoftware@diamond.ac.uk>

"""

import logging
import h5py

from savu.core.utils import logmethod
from savu.plugins.base_loader import BaseLoader

from savu.plugins.utils import register_plugin
import glob
import numpy as np
supported_formats = []
try:
    from PIL import Image
    supported_formats.append('tif')
    supported_formats.append('tiff')
except:
    logging.error("Didn't find Pillow Library. please load/add pillow library to path")
try:
    import pyfits
    supported_formats.append('fits')
except:
    logging.error("Didn't find pyfits library. please load/add pyfits library to path")



class backing_store(object):
    def __init__(self):
        self.filename=""

@register_plugin
class ImageLoader(BaseLoader):
    """
    A class to load fits files
    :param data_file_prefix: file prefix for the data. Default: 'tomo_'
    :param flat_file_prefix: file prefix for the flat field data. Default: 'OB_'
    :param dark_file_prefix: file prefix for the dark field data. Default: 'DC_'
    :param file_suffix: file extension. Default: 'tif'
    :param angles_file: file extension. Default: ''
    """

    def __init__(self, name='ImageLoader'):
        super(ImageLoader, self).__init__(name)

    def setup(self):

        data_obj = self.exp.create_data_object("in_data", "tomo")
        rot = 0
        detY = 1
        detX = 2
        data_obj.set_axis_labels('rotation_angle.degrees',
                                 'detector_y.pixel',
                                 'detector_x.pixel')

        data_obj.add_pattern('PROJECTION', core_dir=(detX, detY),
                             slice_dir=(rot,))
        data_obj.add_pattern('SINOGRAM', core_dir=(detX, rot),
                             slice_dir=(detY,))

        objInfo = data_obj.meta_data
        expInfo = self.exp.meta_data

        data_obj.data, rotation_angle = self.read_images()

        objInfo.set_meta_data("rotation_angle", rotation_angle[...])
        
        data_obj.backing_file = backing_store()
        data_obj.backing_file.filename = 'image_loader.nxs'
        data_obj.set_shape(data_obj.data.shape)
        self.set_data_reduction_params(data_obj)
        print data_obj.data.shape
        print rotation_angle.shape


    def read_angles(self,number_of_angles):
        file_angles = self.parameters['angles_file']
        try:
            file_ptr_angles = open(file_angles,'r')
            angles = file_ptr_angles.readlines()
            angles = [float(i) for i in angles]
            angles = np.asarray(angles)
            return angles
        except:
            angles = np.linspace(0.0,180.0,number_of_angles)
            return angles

          

    def read_images(self):
        """
        This method reads the images using prefix and suffix and returns normalised data
        """
        data_file_prefix = self.parameters['data_file_prefix']
        flat_file_prefix = self.parameters['flat_file_prefix']
        dark_file_prefix = self.parameters['dark_file_prefix']
        extension = self.parameters['file_suffix']
        data = self.read_data(data_file_prefix+"*."+extension, extension)
        flat = self.read_data(flat_file_prefix+"*."+extension, extension)
        dark = self.read_data(dark_file_prefix+"*."+extension, extension)
        #normalise the data
        data = self.normalize(data, flat, dark)
        angles = self.read_angles(data.shape[0])
        return data, angles

    def normalize(self, data, flat, dark):
        if flat is None:
            return data
        if flat.shape[0] != 1:
           #average the flat data
           flat = np.mean(flat,axis=0)
        if dark is None:
           #normalize data using flat
           dark = np.zero(flat.shape)
        if dark.shape[0] != 1:
           #average the dark data
           dark = np.mean(dark,axis=0)
        denom = flat - dark
        denom[denom == 0] = 1e-6
        for m in range(0, data.shape[0]):
            data[m,:,:] = np.true_divide(data[m,: ,:] - dark, denom)
        return data

    def read_data(self, regex, extension):
        data_files_list = glob.glob(regex)
        data_files_list.sort()
        if extension == 'tif' or extension == 'tiff':
            return self.read_data_tiff(data_files_list)
        elif extension == 'fits':
            return self.read_data_fits(data_files_list)
        else:
            logging.error("Doesn't support request Image extension");
        return None

    def read_data_tiff(self, data_files_list):
        data_0 = np.array(Image.open(data_files_list[0]))
        data = np.zeros((len(data_files_list),)+data_0.shape)
        idx = 0
        for data_file_name in data_files_list:
          data_tmp = np.array(Image.open(data_file_name))
          data[idx,:,:] = data_tmp
          idx = idx+1
        return data

    def read_data_fits(self, data_files_list):
        data_0=pyfits.open(data_files_list[0])
        data = np.zeros((len(data_files_list),)+data_0[0].data.shape)
        idx = 0
        for data_file_name in data_files_list:
          data_tmp = pyfits.open(data_file_name)
          data[idx,:,:] = data_tmp[0].data
          idx = idx+1
        return data

