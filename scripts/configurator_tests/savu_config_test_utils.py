# -*- coding: utf-8 -*-
# Copyright 2020 Diamond Light Source Ltd.
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
.. module:: savu_config_test_utils
   :platform: Unix
   :synopsis: unittest test classes for savu_config

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""
import sys

from mock import patch
from io import StringIO

from scripts.config_generator import savu_config

def savu_config_runner(input_list, output_checks,
                       error_str=False):
    """ Run savu_config with a list of input commands

    :param input_list: List of commands for the savu_config
    :param output_checks: List of strings which should be in the
      program output
    :param error_str: If true, then make sure that the error message
     is not displayed inside the output text
    """
    with patch('builtins.input', side_effect=input_list):
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            savu_config.main(test=True)
            output = out.getvalue().strip()
            text_present = any(check in output for check in output_checks)
            if error_str:
                # Check the error text is not present
                error_msg = _get_error_feedback(output, output_checks)
                assert not text_present, error_msg
            else:
                # Check the text is printed to the output
                assert text_present

        finally:
            sys.stdout = saved_stdout

def _get_error_feedback(output, output_checks):
    """Get the error message string

    :param output: Output from savu_config and commands
    :param output_checks: Strings to check for inside the produced output
    :return: error_msg string
    """
    error_list = []
    for line in output.split("\n"):
        if any(check in line for check in output_checks):
            error_list.append(prev_line)
        prev_line = line
    error_msg = "Error in command ouput: \n" + ("\n".join(error_list))
    return error_msg