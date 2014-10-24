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
.. module:: framework_test
   :platform: Unix
   :synopsis: unittest test class for plugin utils

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import unittest
import tempfile
import logging

from savu.core import process
from savu.plugins import utils as pu
from savu.test import test_utils as tu

base_class_name = "savu.plugins.plugin"


class FrameworkTest(unittest.TestCase):

    def setUp(self):
        if not hasattr(self, 'plugin_list'):
            self.plugin_list = [base_class_name]

    def test_pipeline(self):
        logging.debug("Starting test_pipeline")
        if not hasattr(self, 'temp_dir'):
            self.temp_dir = tempfile.gettempdir()
        first_plugin = pu.load_plugin(self.plugin_list[0])
        if self.plugin_list[0] == base_class_name:
            return
        input_data = tu.get_appropriate_input_data(first_plugin)[0]
        logging.debug("Starting to run the processing chain")
        process.run_plugin_chain(input_data, self.plugin_list, self.temp_dir)


class SimpleReconstructionTest(FrameworkTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon"]


class SimpleReconWithRawMedianFilteringTest(FrameworkTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.median_filter",
                            "savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon"]


class SimpleReconWithProjectionMedianFilteringTest(FrameworkTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.median_filter",
                            "savu.plugins.simple_recon"]


class SimpleReconWithVolumeMedianFilteringTest(FrameworkTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.timeseries_field_corrections",
                            "savu.plugins.simple_recon",
                            "savu.plugins.median_filter"]


class SimpleReconWithMedianFilteringTest(FrameworkTest):

    def setUp(self):
        self.plugin_list = ["savu.plugins.median_filter",
                            "savu.plugins.timeseries_field_corrections",
                            "savu.plugins.median_filter",
                            "savu.plugins.simple_recon",
                            "savu.plugins.median_filter"]

if __name__ == "__main__":
    import optparse
    import os
    import sys

    usage = "%prog [options] output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-p", "--plugin", dest="plugin", help="plugin name e.g" +
                      "/path/to/base/plugin.name.including.packages",
                      default="savu.plugins.median_filter",
                      type='string')
    (options, args) = parser.parse_args()

    if len(args) is not 1:
        print "output path needs to be specified"
        sys.exit(1)

    if not os.path.exists(args[0]):
        print("path to output directory %s does not exist" % args[0]);
        sys.exit(2)

    logging.basicConfig(filename=os.path.join(args[0],"log.log"),
                        filemode='w',
                        format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    logging.debug("Files all present and correct")

    suite = unittest.TestSuite()
    ft = FrameworkTest('test_pipeline')
    ft.plugin_list = [options.plugin]
    ft.temp_dir = args[0]
    suite.addTest(ft)

    logging.debug("Test suite setup, ready to run")

    unittest.TextTestRunner().run(suite)

