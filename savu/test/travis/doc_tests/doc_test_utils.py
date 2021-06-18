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
.. module:: doc_test_utils
   :platform: Unix
   :synopsis: A module to set up doc test file handlers
.. moduleauthor:: Jessica Verschoyle

"""
import os
import logging

def add_doc_log_handler(logger, doc_log_path):
    """ Add a file handler to store log output.
    Print errors to the sysout

    :param logger: Logger which we want to add the file handler to
    :param doc_log_path: file path at which to store log file
    """
    filename = os.path.join(doc_log_path, 'doc.log')
    fh = logging.FileHandler(filename, mode='w')
    fh.setFormatter(logging.Formatter('%(message)s'))
    ch = logging.StreamHandler()

    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)

def add_doc_rst_handler(logger, doc_rst_path):
    """ Add a file handler to store rst output.

    :param logger: Logger which we want to add the file handler to
    :param doc_log_path: file path at which to store rst  file
    """
    rst_filename = os.path.join(doc_rst_path, 'doc.rst')
    fh = logging.FileHandler(rst_filename, mode='w')
    fh.setFormatter(logging.Formatter('%(message)s'))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)