
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
        output_checks = ['Close the program']
        sctu.savu_config_runner(input_list, output_checks)

    def testHelpCommand(self):
        input_list = ['help', 'exit', 'y']
        output_checks = ['Display the help information']
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

    def testAddDupl(self):
        # Exception due to invalid plugin number
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'dupl 3',
                      'exit',
                      'y']
        output_checks = ['ValueError']
        sctu.savu_config_runner(input_list, output_checks)

    def testAddDupl_1(self):
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'dupl 1',
                      'exit',
                      'y']
        output_checks = ['Exception', 'Error']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def test_iterate_add_loop_success(self):
        start = 2
        stop = 2
        iterations = 5
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            f"iterate --set {start} {stop} {iterations}",
            'exit',
            'y'
        ]
        output_str = f"The following loop has been added: start plugin index " \
                     f"{start}, end plugin index {stop}, iterations " \
                     f"{iterations}"
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def test_iterate_add_loop_fail(self):
        start = 4
        stop = 4
        iterations = 5
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            f"iterate --set {start} {stop} {iterations}",
            'exit',
            'y'
        ]
        output_str = 'The given plugin indices are not within the range of ' \
            'existing plugin indices'
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def test_iterate_remove_loop_success(self):
        start = 2
        stop = 2
        iterations = 5
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            f"iterate --set {start} {stop} {iterations}",
            'iterate --remove 1',
            'exit',
            'y'
        ]
        output_str = f"The following loop has been removed: start plugin " \
                     f"index {start}, end plugin index {stop}, iterations " \
                     f"{iterations}"
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def test_iterate_remove_loop_fail(self):
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            'iterate --remove 1',
            'exit',
            'y'
        ]
        output_str = "There doesn't exist an iterative loop with number 1"
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def test_iterate_remove_all_loops_confirm(self):
        start = 2
        stop = 2
        iterations = 5
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            f"iterate --set {start} {stop} {iterations}",
            'iterate --remove',
            'y',
            'exit',
            'y'
        ]
        output_str = 'All iterative loops have been removed'
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def test_iterate_remove_all_loops_deny(self):
        start = 2
        stop = 2
        iterations = 5
        input_list = [
            'add TomoPhantomLoader',
            'add MedianFilter',
            f"iterate --set {start} {stop} {iterations}",
            'iterate --remove',
            'n',
            'exit',
            'y'
        ]
        output_str = 'No iterative loops have been removed'
        output_checks = [output_str]
        sctu.savu_config_runner(input_list, output_checks)

    def testReplace(self):
        # Exception due to invalid plugin number
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'replace 2 TomopyRecon',
                      'exit',
                      'y']
        output_checks = ['ValueError']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testReplace_1(self):
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'replace 1 SavuNexusLoader',
                      'exit',
                      'y']
        output_checks = ['Exception', 'Error']
        sctu.savu_config_runner(input_list, output_checks,
                                error_str=True)

    def testReplace_2(self):
        input_list = ['add NxtomoLoader',
                      'add AstraReconCpu',
                      'replace 1 IncorrectString',
                      'exit',
                      'y']
        output_checks = ['Unknown plugin']
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
