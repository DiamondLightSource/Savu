
"""
.. module:: savu_config_test
   :platform: Unix
   :synopsis: unittest test for savu_config
.. moduleauthor: Mark Basham

"""

from __future__ import print_function

import sys
import unittest
from mock import patch
from StringIO import StringIO

from scripts.config_generator import savu_config


class SavuConfigTest(unittest.TestCase):

    def savu_config_runner(self, input_list, output_checks,
                           error_str=False):
        """ Run savu_config with a list of input commands

        :param input_list: List of commands for the savu_config
        :param output_checks: List of strings which should be in the
          program output
        :param error_str: If true, then make sure that the error message
         is not displayed inside the output text
        """
        with patch('__builtin__.raw_input', side_effect=input_list):
            saved_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out
                savu_config.main()
                output = out.getvalue().strip()
                for check in output_checks:
                    if error_str:
                        assert check not in output
                    else:
                        assert check in output

            finally:
                sys.stdout = saved_stdout

    def testExit(self):
        input_list = ['exit', 'y']
        output_checks = ['Thanks for using the application']
        self.savu_config_runner(input_list, output_checks)

    def testHelpBlank(self):
        input_list = ['', 'exit', 'y']
        output_checks = ['help :  Display the help information',
                         'exit :  Close the program']
        self.savu_config_runner(input_list, output_checks)

    def testHelpCommand(self):
        input_list = ['help', 'exit', 'y']
        output_checks = ['help :  Display the help information',
                         'exit :  Close the program']
        self.savu_config_runner(input_list, output_checks)

    def testAdd(self):
        input_list = ['add NxtomoLoader',
                      'exit',
                      'y']
        output_checks = ['Exception']
        self.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod(self):
        input_list = ['add NxtomoLoader',
                      'disp',
                      'mod 1.3 Test text',
                      'exit',
                      'y']
        output_checks = ['Exception']
        self.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod_2(self):
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'mod 1.4 FBP',
                      'exit',
                      'y']
        output_checks = ['Exception']
        self.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod_3(self):
        # Exception due to invalid parameter number
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'mod 1.45 FBP',
                      'exit',
                      'y']
        output_checks = ['Exception']
        self.savu_config_runner(input_list, output_checks)


if __name__ == "__main__":
    unittest.main()
