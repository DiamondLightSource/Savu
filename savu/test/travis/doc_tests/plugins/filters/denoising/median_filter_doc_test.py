
"""
.. module:: median_filter_doc_test
   :platform: Unix
   :synopsis: unittest test for plugin restructured text file documentation
.. moduleauthor: Jessica Verschoyle

"""

import os
import sys
import unittest
import logging
import logging.config

from io import StringIO

import savu.plugins.utils as pu
import savu.test.travis.doc_tests.doc_test_utils as dtu
import scripts.configurator_tests.savu_config_test_utils as sctu
import scripts.configurator_tests.refresh_process_lists_test as refresh

# Determine Savu base path
main_dir = \
    os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
savu_base_path = f"{main_dir}/Savu/"

class MedianFilterDocTest(unittest.TestCase):

    def setUp(self):
        """ Set up file handlers for the log and rst file.

        :param out_path: The file path to the directory to save to
        """
        self.setup_argparser()
        doc_test_path = "savu/test/travis/doc_tests/"
        plugin_log_file = f"{doc_test_path}logs"  \
                          f"/filters/denoising/median_filter/"
        out_path = savu_base_path + plugin_log_file
        # Create directory if it doesn't exist
        pu.create_dir(out_path)

        logging.config.fileConfig(
            savu_base_path + doc_test_path + "logging.conf")

        logger = logging.getLogger("documentationLog")
        dtu.add_doc_log_handler(logger, out_path)

        logger_rst = logging.getLogger("documentationRst")
        dtu.add_doc_rst_handler(logger_rst, out_path)

        print("The log files are inside the directory "+out_path)
    
    def setup_argparser(self):
        """ Clean sys.argv so that command line testing will complete"""
        import sys
        sys.argv = ['']
        del sys
            
    def test_median_filter_doc(self):
        """ Run the input commands with savu_config
        """
        
        input_list = ["add MedianFilter",
                      "mod 1.1 6",
                      "mod 1.3 2D",
                      "disp -a",
                      "exit", "y"]
        output_checks = ["Exception","Error","ERROR"]
        sctu.savu_config_runner(input_list, output_checks, 
                                error_str=True)
    
if __name__ == "__main__":
    unittest.main()
    