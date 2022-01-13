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
.. module:: savu_refresh_process_lists
   :platform: Unix
   :synopsis:

.. moduleauthor:: Jessica Verschoyle <scientificsoftware@diamond.ac.uk>

"""
import os
import argparse

from colorama import Style

import scripts.config_generator.config_utils as cu
from scripts.config_generator.content import Content
from scripts.config_generator.config_utils import error_catcher_savu


def __option_parser(doc=True):
    """Option parser for command line arguments."""
    desc = "Refresh process lists to update their parameter and " \
           "citation information with the most recent version of Savu."
    parser = argparse.ArgumentParser(prog="savu_refresh", description=desc)
    # Require at least one of the optional arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file",
                        help="The process list file to be refreshed",
                        action="store", type=str)
    dir_str = "Refresh all process list files inside this directory"
    group.add_argument("-d", "--directory", help=dir_str,
                        action="store", type=str)
    return parser if doc is True else parser.parse_args()


def refresh_process_file(path):
    """Refresh the process list file at path provided"""
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


def refresh_file(f):
    """Refresh the process list file at path f"""
    c_on = Style.BRIGHT
    c_off = Style.RESET_ALL
    if os.path.isfile(f):
        if f.endswith(".nxs") or f.endswith(".savu"):
            try:
                refresh_process_file(os.path.abspath(f))
            except IOError:
                print(f"{c_on}ERROR: Problem refreshing {f} \n"
                      f"Please make sure that this is a valid Savu "
                      f"process list.{c_off}")

    else:
        print("File not found")


@error_catcher_savu
def refresh_lists():
    """Refresh the directory or process list file provided
    Use a decorator to hide the error traceback
    """
    args = __option_parser(doc=False)
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
        cu.populate_plugins()
        for f in os.listdir(folder):
            print(f"Refreshing {f}")
            refresh_file(os.path.abspath(folder + "/" + f))
        print("*****************   Refresh complete   ****************")

    elif args.file:
        if not os.path.isfile(args.file):
            raise ValueError("Please enter a valid filepath.")
        cu.populate_plugins()
        print(f"Refreshing {args.file}")
        refresh_file(args.file)
        print("*****************   Refresh complete   ****************")


