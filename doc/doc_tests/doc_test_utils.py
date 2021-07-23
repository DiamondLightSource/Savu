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

import savu.plugins.utils as pu


def setup_argparser():
    """ Clean sys.argv so that command line testing will complete"""
    import sys

    sys.argv = [""]
    del sys


def get_loggers():
    logger = logging.getLogger("documentationLog")
    logger_rst = logging.getLogger("documentationRst")
    return logger, logger_rst


def doc_test_path_setup(plugin_dir):
    """Setup the logging file path, the logging config path and create the
    relevant directories
    """

    # Determine Savu base path
    main_dir = os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
    savu_base_path = f"{main_dir}/Savu/"

    doc_test_path = "doc/doc_tests/"
    plugin_log_file = f"{doc_test_path}logs{plugin_dir}"
    out_path = savu_base_path + plugin_log_file

    config_path = f"{savu_base_path}{doc_test_path}logging.conf"

    # Create directory if it doesn't exist
    pu.create_dir(out_path)
    return out_path, config_path


def setup_log_files(logger, logger_rst, path):
    """Use the logging config file to set up the log handlers,
    the format of the messages, and the 'level' eg DEBUG or CRITICAL

    :param logger: logger object for log file
    :param logger_rst: logger object for rst file
    :param path: path for documentation test logs
    :return:
    """
    out_path, config_path = doc_test_path_setup(path)
    logging.config.fileConfig(config_path)

    # Add handlers to the logger to tell it where to send the log
    # information
    fh, ch = add_doc_log_handler(logger, out_path)
    fh_rst = add_doc_rst_handler(logger_rst, out_path)

    print("The log files are inside the directory " + out_path)
    return fh, ch, fh_rst


def add_doc_log_handler(logger, doc_log_path):
    """Add a file handler to store the logger output to a file.
    Add a stream handler to send the logger output to the
    command line/sys output.

    :param logger: Logger which we want to add the file handler to
    :param doc_log_path: file path at which to store log file
    :returns file and stream handlers
    """
    filename = os.path.join(doc_log_path, "doc.log")
    fh = logging.FileHandler(filename, mode="w")
    fh.setFormatter(logging.Formatter("%(message)s"))
    ch = logging.StreamHandler()

    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return fh, ch


def add_doc_rst_handler(logger, doc_rst_path):
    """Add a file handler to store the logger output to a file.

    :param logger: Logger which we want to add the handler to
    :param doc_log_path: file path at which to store rst file
    :return file handler
    """
    rst_filename = os.path.join(doc_rst_path, "doc.rst")
    fh = logging.FileHandler(rst_filename, mode="w")
    fh.setFormatter(logging.Formatter("%(message)s"))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return fh


def close_handler(logger, handler):
    """Close handler"""
    handler.close()
    logger.removeHandler(handler)


def end_logging(logger, logger_rst, fh, ch, fh_rst):
    """Close open handlers. Shutdown logging operation.

    :param logger: The logger for the log file and command line output
    :param logger_rst: The logger for the rst file
    :param fh: Tile handler for log file
    :param ch: Stream handler for command line
    :param fh_rst: File handler for rst file
    """
    close_handler(logger, fh)
    close_handler(logger, ch)
    close_handler(logger_rst, fh_rst)
    logging.shutdown()
