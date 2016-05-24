'''
Created on 24 May 2016

@author: ssg37927
'''
import unittest
from mock import patch
import __builtin__
import savu_config

from contextlib import contextmanager

@contextmanager
def mockRawInput(mock):
    original_raw_input = __builtin__.raw_input
    __builtin__.raw_input = lambda _: mock
    yield
    __builtin__.raw_input = original_raw_input


class Test(unittest.TestCase):


    def testName(self):
        with patch('__builtin__.raw_input', side_effect=['exit', 'y']):
            savu_config.main()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()