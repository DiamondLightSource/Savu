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
.. module:: base_driver
   :platform: Unix
   :synopsis: Base class or all driver plugins

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging
from mpi4py import MPI


class BaseDriver(object):
    """
    The base class from which all driver plugins should inherit.
    """

    def get_communicator(self):
        """
        This method should return an MPI communicator
        """
        logging.error("get_communicator needs to be implemented")
        raise NotImplementedError("get_communicator needs to be implemented.")

    def plugin_barrier(self):
        return self.exp._barrier(communicator=self.get_communicator())

    def _run_plugin_instances(self, transport, communicator=MPI.COMM_WORLD):
        """ Runs the pre_process, process and post_process methods.

        If parameter tuning is required, loop over the methods and set the
        correct parameters for each run. """

        self.__set_communicator(communicator)

        logging.info("%s.%s", self.__class__.__name__, 'pre_process')
        self.base_pre_process()
        self.pre_process()
        logging.info("%s.%s", self.__class__.__name__, '_barrier')
        self.plugin_barrier()

        logging.info("%s.%s", self.__class__.__name__, 'process_frames')
        transport._transport_checkpoint(transport._transport_process(self))

        logging.info("%s.%s", self.__class__.__name__, '_barrier')
        self.plugin_barrier()

        logging.info("%s.%s", self.__class__.__name__, 'post_process')
        self.post_process()
        self.base_post_process()    
