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
.. module:: tomo_recon
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import optparse

from savu.core import process

from savu.data.process_data import ProcessList

import savu.plugins.utils as pu

if __name__ == '__main__':

    usage = "%prog [options] input_file output_directory"
    version = "%prog 0.1"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-n", "--names", dest="names", help="Process names",
                      default="CPU1,CPU2,CPU3,CPU4,CPU5,CPU6,CPU7,CPU8",
                      type='string')
    parser.add_option("-f", "--filename", dest="process_filename",
                      help="The filename of the process file",
                      default="/home/ssg37927/Savu/test_data/process01.nxs",
                      type='string')
    (options, args) = parser.parse_args()

    logging.info("Starting tomo_recon process")

    # TODO Check all the files at this point

    process_filename = options.process_filename

    process_list = ProcessList()
    process_list.populate_process_list(process_filename)

    first_plugin = pu.load_plugin(None, process_list.process_list[0]['id'])
    input_data = pu.load_raw_data(args[0])

    process.run_process_list(input_data, process_list, args[1])
