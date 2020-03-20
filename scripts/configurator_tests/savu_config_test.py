'''
Created on 24 May 2016

@author: ssg37927
'''


import sys
import unittest
from mock import patch
from io import StringIO

from scripts.config_generator import savu_config


class Test(unittest.TestCase):

    def savu_config_runner(self, input_list, output_checks):
        with patch('builtins.input', side_effect=input_list):

            saved_stdout = sys.stdout
            try:
                out = StringIO()
                sys.stdout = out
                savu_config.main(test=True)
                output = out.getvalue().strip()
                for check in output_checks:
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

if __name__ == "__main__":
    unittest.main()
