
"""
.. module:: projection_shift_doc_test
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
                                     "/alignment/projection_shift/")
                                     
class ProjectionShiftDocTest(unittest.TestCase):

    def refresh_process_lists(self):
        """ Run through the process list files and refresh them to update
        any inconsistent parameter values.
        If there is a value which cannot be used, that parameter will 
        be set to the default value.
        """
        process_lists = ["test_data/process_lists/vo_centering_process.nxs",
                         "test_data/process_lists/vo_centering_test.nxs"]
        output_checks = ["Exception","Error","ERROR"]
        for process_list_path in process_lists:
            file_exists = os.path.exists(savu_base_path + process_list_path)
            error_msg = f"The process list at {process_list_path}" \
                        f"does not exist."
            
            self.assertTrue(file_exists, msg=error_msg)
            if file_exists:
                # Write the process list being tested to the logger
                logger.debug(f"REFRESH PROCESS LIST: " \
                             f"{savu_base_path}{process_list_path}")
                saved_stdout = sys.stdout
                try:
                    out = StringIO()
                    sys.stdout = out
                    refresh.generate_test(savu_base_path \
                                              + process_list_path)
                    output_value = out.getvalue().strip()
                    for check in output_checks:
                        error_msg = f"Refresh failed: {check} in the output."
                        assert check not in output_value, error_msg
                finally:
                    sys.stdout = saved_stdout
            
    def test_projection_shift_doc(self):
        """ Run the input commands with savu_config
        """
        self.refresh_process_lists()
        input_list = ["add NxtomoLoader",
                      "mod 1.1 []",
                      "disp -a",
                      "add ProjectionShift",
                      "disp 1.3 -vv",
                      "open /home/glb23482/git_projects/Savu/test_data/process_lists/vo_centering_process.nxs",
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
    