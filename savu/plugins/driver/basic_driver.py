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
.. module:: basic_driver
   :platform: Unix
   :synopsis: Base class or all driver plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
from mpi4py import MPI


class BasicDriver(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(BasicDriver, self).__init__()

    def get_mem_multiply(self):
        return 1

    def _run_plugin_instances(self, transport, communicator=MPI.COMM_WORLD):
        self.__set_communicator(communicator)
        logging.info("%s.%s", self.__class__.__name__, 'pre_process')
        self.base_pre_process()
        self.pre_process()

        msg = "Pre-process completed for %s" % self.__class__.__name__
        self.plugin_barrier(msg=msg)

        logging.info("%s.%s", self.__class__.__name__, 'process_frames')
        transport._transport_process(self)

        msg = "Process_frames completed for %s" % self.__class__.__name__
        self.plugin_barrier(msg=msg)

        logging.info("%s.%s", self.__class__.__name__, 'post_process')
        self.post_process()
        self.base_post_process()

    def __set_communicator(self, comm):
        self._communicator = comm

    def get_communicator(self):
        return self._communicator

    def plugin_barrier(self, msg=''):
        return self.exp._barrier(communicator=self.get_communicator(), msg=msg)
