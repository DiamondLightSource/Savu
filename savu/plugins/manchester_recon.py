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
.. module:: manchester_recon
   :platform: Unix
   :synopsis: An implementation of the Manchester code

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
from savu.data.process_data import CitationInfomration
from savu.data.structures import ProjectionData, VolumeData
from savu.plugins.gpu_filter import GpuFilter

import subprocess
import os
import logging

from xml.dom.minidom import parse


class ManchesterRecon(GpuFilter):
    """
    A Plugin to apply a simple reconstruction with no dependancies
    """

    def __init__(self):
        super(ManchesterRecon, self).__init__("SimpleRecon")

    def populate_default_parameters(self):
        self.parameters['center_of_rotation'] = 83

    def filter_frame(self, data):
        """
        Process the frame with the manchester code

        :param data: The data to filter
        :type data: ndarray
        :returns:  The filtered image
        """
        centre_of_rotation = self.parameters['center_of_rotation']

        # Save out Sinograms

        # Call processinng

        # load in reconstructions

        return None

    def required_data_type(self):
        """
        The input for this plugin is ProjectionData

        :returns:  ProjectionData
        """
        return ProjectionData

    def output_data_type(self):
        """
        The output of this plugin is VolumeData

        :returns:  VolumeData
        """
        return VolumeData

    def get_citation_inforamtion(self):
        cite_info = CitationInfomration()
        cite_info.description = \
            ("TO POPULATE")
        cite_info.bibtex = \
            ("TO POPULATE")
        cite_info.endnote = \
            ("TO POPULATE")
        cite_info.doi = "TO POPULATE"
        return cite_info

    def _set_gpu_device_number(self, input_xml_dom, gpu_number):
        element = input_xml_dom.getElementsByTagName('GPUDeviceNumber')[0]
        element.childNodes[0].nodeValue = gpu_number

    def _set_sino_filename(self, input_xml_dom, folder, prefix, extension,
                               number_of_digits, first_file, last_file,
                               file_step):
        element = input_xml_dom.getElementsByTagName("InputData")[0]
        element.getElementsByTagName("Folder")[0].childNodes[0].nodeValue =\
            folder
        element.getElementsByTagName("Prefix")[0].childNodes[0].nodeValue =\
            prefix
        element.getElementsByTagName("Extension")[0].childNodes[0].nodeValue =\
            extension
        element.getElementsByTagName("NOD")[0].childNodes[0].nodeValue =\
            number_of_digits
        element.getElementsByTagName("FileFirst")[0].childNodes[0].nodeValue =\
            first_file
        element.getElementsByTagName("FileLast")[0].childNodes[0].nodeValue =\
            last_file
        element.getElementsByTagName("FileStep")[0].childNodes[0].nodeValue =\
            file_step

    def _set_recon_filename(self, input_xml_dom, folder, prefix, extension,
                            number_of_digits):
        element = input_xml_dom.getElementsByTagName("OutputData")[0]
        element.getElementsByTagName("Folder")[0].childNodes[0].nodeValue =\
            folder
        element.getElementsByTagName("Prefix")[0].childNodes[0].nodeValue =\
            prefix
        element.getElementsByTagName("Extension")[0].childNodes[0].nodeValue =\
            extension
        element.getElementsByTagName("NOD")[0].childNodes[0].nodeValue =\
            number_of_digits

    def _set_recon_centre(self, input_xml_dom, recon_centre):
        element = input_xml_dom.getElementsByTagName("ImageCentre")[0]
        element.childNodes[0].nodeValue = recon_centre

    def _set_recon_range(self, input_xml_dom, recon_range):
        element = input_xml_dom.getElementsByTagName("Transform")[0]
        element.getElementsByTagName("RotationAngleType")[0].\
            childNodes[0].nodeValue = 'Other'
        element.getElementsByTagName("RotationAngle")[0].\
            childNodes[0].nodeValue = recon_range

    def _set_recon_rotation(self, input_xml_dom, recon_rotation):
        element = input_xml_dom.getElementsByTagName("ROI")[0]
        element.getElementsByTagName("Angle")[0].childNodes[0].nodeValue =\
            recon_rotation

    def _process_from_sinogram(self, sino_prefix, sino_number, centre,
                               output_directory,
                               template_xml_file="/home/ssg37927/I12/tomotest/chunk_002.xml",
                               gpu_number=0, recon_range=180.0,
                               recon_rotation=0.0):
        self._process_multiple_from_sinogram(sino_prefix, sino_number,
                                             sino_number, 1, centre,
                                             output_directory,
                                             template_xml_file, gpu_number,
                                             recon_range, recon_rotation)

    def _process_multiple_from_sinogram(self, sino_prefix, sino_start,
                                        sino_end, sino_step, centre,
                                        output_directory,
                                        template_xml_file="/home/ssg37927/I12/tomotest/chunk_002.xml",
                                        gpu_number=0, recon_range=180.0,
                                        recon_rotation=0.0):
        # construct the input file
        dom = parse(template_xml_file)

        self._set_gpu_device_number(dom, gpu_number)

        tmpdir = os.getenv('TMPDIR')

        logging.debug("tempdir = %s", tmpdir)
        self._set_sino_filename(dom, tmpdir, sino_prefix, "tif", 5,
                                   sino_start, sino_end, sino_step)
        self._set_recon_range(dom, recon_range)
        self._set_recon_rotation(dom, recon_rotation)
        if centre < -9000:
            print("No centre set, using default")
            self._set_recon_filename(dom, output_directory, "recon_", "tif", 5)
        else:
            self._set_recon_filename(dom, output_directory,
                                     "recon_%06i_" % (int(centre*100)), "tif",
                                     5)
            self._set_recon_centre(dom, centre)

        xml_filename = tmpdir+"/input%05i.xml" % sino_start
        fh = open(xml_filename, 'w')
        dom.writexml(open(xml_filename, 'w'))
        fh.close()

        # actually call the program
        log_location = '/dls/tmp/tomopy/dt64/%i${USER}test.out' % (sino_start)
        command = \
            (". /etc/profile.d/modules.sh;" +
             " module load i12;" +
             " export CUDA_CACHE_DISABLE=1;" +
             " echo BEFORE;" +
             " dt64n %s &> %s;" % (xml_filename, log_location) +
             " echo AFTER")
        logging.debug("COMMAND CALLED'" + command + "'")
        subprocess.call([command], shell=True)
