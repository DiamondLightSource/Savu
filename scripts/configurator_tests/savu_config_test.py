
"""
.. module:: savu_config_test
   :platform: Unix
   :synopsis: unittest test for savu_config
.. moduleauthor: Mark Basham

"""

import unittest
from mock import patch
from io import StringIO
import subprocess

from scripts.config_generator import savu_config

import scripts.configurator_tests.savu_config_test_utils as sctu

class SavuConfigTest(unittest.TestCase):

    def testExit(self):
        input_list = ['exit', 'y']
        output_checks = ['Thanks for using the application']
        sctu.savu_config_runner(input_list, output_checks)

    def testHelpBlank(self):
        input_list = ['', 'exit', 'y']
        output_checks = ['help :  Display the help information',
                         'exit :  Close the program']
        sctu.savu_config_runner(input_list, output_checks)

    def testHelpCommand(self):
        input_list = ['help', 'exit', 'y']
        output_checks = ['help :  Display the help information',
                         'exit :  Close the program']
        sctu.savu_config_runner(input_list, output_checks)

    def testAdd(self):
        input_list = ['add NxtomoLoader',
                      'exit',
                      'y']
        output_checks = ['Exception']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod(self):
        input_list = ['add NxtomoLoader',
                      'disp',
                      'mod 1.3 Test text',
                      'exit',
                      'y']
        output_checks = ['Exception']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod_2(self):
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'mod 1.4 FBP',
                      'exit',
                      'y']
        output_checks = ['Exception']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testAddMod_3(self):
        # Exception due to invalid parameter number
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'mod 1.45 FBP',
                      'exit',
                      'y']
        output_checks = ['Exception']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testrunconfig(self):
        result = subprocess.run(['savu_config', '-h'], stdout=subprocess.PIPE)
        str_stdout=str(result.stdout)
        if "Create" not in str_stdout:
            # Savu_config has failed to load
            assert False


if __name__ == "__main__":
    unittest.main()
