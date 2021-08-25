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
.. module:: mtf_deconvolution
   :platform: Unix
   :synopsis: A plugin for MTF (modulation transfer function) deconvolution or \
    PSF (point spread function) correction in the Fourier domain.
.. moduleauthor:: Nghia Vo <scientificsoftware@diamond.ac.uk>

"""
import os
import logging
import numpy as np
from PIL import Image
import pyfftw.interfaces.scipy_fftpack as fft
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin
from savu.data.plugin_list import CitationInformation
import savu.test.test_utils as tu
import savu.core.utils as cu



@register_plugin
class MtfDeconvolution(Plugin, CpuPlugin):

    def __init__(self):
        super(MtfDeconvolution, self).__init__("MtfDeconvolution")

    def load_image(self, file_path):
        """
        Load data from an image.
        """
        mat = None
        try:
            mat = np.asarray(Image.open(file_path), dtype = np.float32)
        except IOError:
            raise ValueError("No such file or directory {}".format(file_path))
        if len(mat.shape) > 2:
            axis_m = np.argmin(mat.shape)
            mat = np.mean(mat, axis=axis_m)
        return mat

    def check_file_path(self, file_path):
        file_ext = ".tif"
        if file_path is None:
            msg = "!!! Please provide a file path to the MTF !!!"
            logging.warning(msg)
            cu.user_message(msg)
            raise ValueError(msg)
        else:
            if not os.path.isfile(file_path):
                msg = "!!! No such file: %s !!!"\
                        " Please check the file path" %str(file_path)
                logging.warning(msg)
                cu.user_message(msg)
                raise ValueError(msg)
            else:
                _, file_ext = os.path.splitext(file_path)
        return file_ext

    def psf_correction(self, mat, win, pad_width):
        (nrow, ncol) = mat.shape
        mat_pad = np.pad(mat, pad_width, mode = "reflect")
        win_pad = np.pad(win, pad_width, mode = "constant", constant_values=1.0)
        mat_dec = fft.ifft2(fft.fft2(mat_pad) / fft.ifftshift(win_pad))
        return np.abs(mat_dec)[pad_width:pad_width+nrow,pad_width:pad_width+ncol]

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0], raw=True)
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('PROJECTION','single')
        out_pData[0].plugin_data_setup('PROJECTION','single')

    def pre_process(self):
        inData = self.get_in_datasets()[0]
        dark = inData.data.dark()
        flat = inData.data.flat()
        self.data_size = inData.get_shape()
        (self.depth, self.height, self.width) = flat.shape
        file_path = self.get_conf_path()
        file_ext = self.check_file_path(file_path)
        if file_ext==".npy":
            try:
                self.mtf_array = 1.0*np.load(file_path)
            except IOError:
                msg = "\n*****************************************\n"\
                    "!!! ERROR !!! -> Can't open this file: %s \n"\
                    "*****************************************\n\
                    " % str(file_path)
                logging.warning(msg)
                cu.user_message(msg)
                raise ValueError(msg)
        else:
            try:
                self.mtf_array = 1.0*np.float32(self.load_image(file_path))
            except IOError:
                msg = "\n*****************************************\n"\
                    "!!! ERROR !!! -> Can't open this file: %s \n"\
                    "*****************************************\n\
                    " % str(file_path)
                logging.warning(msg)
                cu.user_message(msg)
                raise ValueError(msg)

        self.mtf_array[self.mtf_array<=0.0] = 1.0
        self.mtf_array = self.mtf_array/np.max(self.mtf_array)
        (height_mtf, width_mtf) = self.mtf_array.shape
        if (self.height != height_mtf) or (self.width != width_mtf):
            msg = "\n*****************************************\n"\
            "!!! ERROR !!!-> Projection shape: ({0},{1}) is not the same as "\
            "the mtf shape: ({2},{3})".format(
                self.height, self.width, height_mtf, width_mtf)
            logging.warning(msg)
            cu.user_message(msg)
            raise ValueError(msg)

        self.pad_width = np.clip(int(self.parameters["pad_width"]), 0, None)
        if flat.size:
            flat_updated = np.ones_like(flat, dtype=np.float32)
            for i in np.arange(self.depth):
                flat_updated[i] = self.psf_correction(
                    flat[i], self.mtf_array, self.pad_width)
            inData.data.update_flat(flat_updated)

    def process_frames(self, data):
        return self.psf_correction(data[0], self.mtf_array, self.pad_width)

    def get_conf_path(self):
        path = self.parameters["file_path"]
        if path.split(os.sep)[0] == 'Savu':
            path = tu.get_test_data_path(path.split('/test_data/data')[1])
        return path

    def get_citation_information(self):
        cite_info = CitationInformation()
        cite_info.description = \
            ("The PSF correction used in this plugin is taken\
             from this work.")
        cite_info.bibtex = ("@inproceedings{10.1117/12.2530324,\n"\
            "author = {Nghia T. Vo and Robert C. Atwood "\
            "and Michael Drakopoulos},\n"\
            "title = {{Preprocessing techniques for removing artifacts in "\
            "synchrotron-based tomographic images}},\n"\
            "volume = {11113},\n"\
            "booktitle = {Developments in X-Ray Tomography XII},\n"\
            "editor = {Bert Muller and Ge Wang},\n"\
            "organization = {International Society for Optics and Photonics},\n"\
            "publisher = {SPIE},\n"\
            "pages = {309 -- 328},\n"\
            "year = {2019},\n"\
            "doi = {10.1117/12.2530324},\n"\
            "URL = {https://doi.org/10.1117/12.2530324}\n"\
            "}")
        cite_info.doi = "doi: DOI: 10.1117/12.2530324"
        return cite_info
