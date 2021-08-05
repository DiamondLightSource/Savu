
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

import doc.doc_tests.doc_test_utils as dtu
import scripts.configurator_tests.savu_config_test_utils as sctu
import scripts.configurator_tests.refresh_process_lists_test as refresh

# Determine Savu base path
main_dir = \
    os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
savu_base_path = f"{main_dir}/Savu/"

# Reset the args for command line input
dtu.setup_argparser()

# Start logging
logger, logger_rst = dtu.get_loggers()
fh, ch, fh_rst = dtu.setup_log_files(logger, logger_rst,
                                     "/filters/denoising/median_filter/")
                                     
class MedianFilterDocTest(unittest.TestCase):
    
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
    
    def tearDown(self):
        # End the logging session
        dtu.end_logging(logger, logger_rst, fh, ch, fh_rst)
        logging.shutdown()

if __name__ == "__main__":
    unittest.main()
    