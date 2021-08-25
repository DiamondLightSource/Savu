# -*- coding: utf-8 -*-
# Copyright 2014 Diamond Light Source Ltd.
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
.. module:: refresh_process_lists_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import os
import argparse
import unittest

from colorama import Style

import savu.test.test_process_list_utils as tplu
import scripts.config_generator.config_utils as cu
from scripts.config_generator.content import Content


def __option_parser(doc=True):
    """Option parser for command line arguments."""
    parser = argparse.ArgumentParser(prog="savu_refresh")
    # Require at least one of the optional arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file",
                        help="The process list file to be refreshed",
                        action="store", type=str)
    dir_str = "Refresh all process list files inside this directory"
    group.add_argument("-d", "--directory", help=dir_str,
                        action="store", type=str)
    return parser if doc is True else parser.parse_args()


class RefreshProcessListsTest(unittest.TestCase):
    def _refresh_process_file(self, path):
        content = Content()
        # open
        content.fopen(path, update=True)
        # refresh
        positions = content.get_positions()
        for pos_str in positions:
            content.refresh(pos_str)
        # save
        content.save(content.filename)
        print("Content has been saved")


def generate_test(path):
    def test(self):
        self._refresh_process_file(path)

    return test


def _under_revision(path):
    files = tplu.get_test_process_list(
        path + 'test_data/test_process_lists/under_revision')
    return ['under_revision/' + f for f in files]


def refresh_unittest():
    path = os.path.dirname(os.path.realpath(__file__)).split("scripts")[0]

    nxs_in_tests, plugins_in_tests = \
        tplu.get_process_list(path + '/savu/test')

    lists = tplu.get_test_process_list(path + 'test_data/process_lists') \
        + tplu.get_test_process_list(path+'test_data/test_process_lists')
    nxs_used = list(set(nxs_in_tests).intersection(set(lists)))

    test_path = path + "/test_data/test_process_lists"
    test_path2 = path + "/test_data/process_lists"

    exclude = ["multimodal/simple_fit_test_XRF.nxs"] + _under_revision(path)

    for f in [n for n in nxs_used if n not in exclude]:
        print("Refreshing process list", f, "...")
        if os.path.exists(os.path.join(test_path, f)):
            path = os.path.join(test_path, f)
        else:
            path = os.path.join(test_path2, f)

        # generates a function that calls refresh_process_file for each file
        test = generate_test(path)
        # then sets the function as an attribute of the test class, so that
        # every process list is ran as an independent test
        setattr(RefreshProcessListsTest, f"test_{path}", test)
    unittest.main()


def refresh_file(f):
    """Refresh the process list file at path f"""
    c_on = Style.BRIGHT
    c_off = Style.RESET_ALL
    if os.path.isfile(f):
        if f.endswith(".nxs") or f.endswith(".savu"):
            try:
                RefreshProcessListsTest()._refresh_process_file(
                    os.path.abspath(f)
                )
            except IOError:
                print(f"{c_on}ERROR: Problem refreshing {f} \n"
                      f"Please make sure that this is a valid Savu "
                      f"process list.{c_off}")

    else:
        print("File not found")


def refresh_lists():
    """Refresh the directory or process list file provided"""
    args = __option_parser(doc=False)
    cu.populate_plugins()
    if args.directory:
        # Append a final backslash
        in_directory = os.path.join(args.directory,"")
        if not os.path.isdir(in_directory):
            raise ValueError("Please enter a valid directory.")
        print("\n*******************************************************")
        print(f"Refreshing all process lists found within the"
              f"\ndirectory {in_directory}")
        print("*******************************************************")
        folder = os.path.dirname(in_directory)
        for f in os.listdir(folder):
            print(f"Refreshing {f}")
            refresh_file(os.path.abspath(folder + "/" + f))
        print("*****************   Refresh complete   ****************")

    elif args.file:
        if not os.path.isfile(args.file):
            raise ValueError("Please enter a valid filepath.")
        print(f"Refreshing {args.file}")
        refresh_file(args.file)
        print("*****************   Refresh complete   ****************")


if __name__ == "__main__":
    cu.populate_plugins()
    refresh_unittest()
