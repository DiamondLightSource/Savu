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
.. module:: savu_config_utils
   :platform: Unix
   :synopsis: unittest test classes for savu_config

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""
import sys

from mock import patch
from StringIO import StringIO

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
    with patch('__builtin__.raw_input', side_effect=input_list):
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            savu_config.main()
            output = out.getvalue().strip()
            for check in output_checks:
                if error_str:
                    error_msg = 'Command failed: '+ check +' in the output.'
                    assert check not in output, error_msg
                else:
                    assert check in output
        finally:
            sys.stdout = saved_stdout