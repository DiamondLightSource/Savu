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
.. module:: base_saver
   :platform: Unix
   :synopsis: A base class for all saver plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import logging
import os
import h5py
from mpi4py import MPI

from savu.plugins.plugin import Plugin


class BaseSaver(Plugin):
    """
    A base plugin from which all data saver plugins should inherit.
    """
    def __init__(self, name="BaseSaver"):
        super(BaseSaver, self).__init__(name)
        self.nxs_filename = None
        self.nxs_file = None

    def _main_setup(self, exp, params):
        """
        Overwrites the main_setup function in plugin.py as the saver is a
        special case of plugin that doesn't required setup of in/out_datasets
        """
        self.exp = exp
        logging.info("%s.%s", self.__class__.__name__, 'setup')
        self._create_nxs_file(self.exp.meta_data.get('out_path'))

    def _create_nxs_file(self, folder):
        fname = os.path.basename(folder.split('_')[-1]) + '_processed.nxs'
        filename = os.path.join(folder, fname)
        self.nxs_filename = filename
        if self.exp.meta_data.get("mpi") is True:
            self.nxs_file = h5py.File(filename, 'w', driver='mpio',
                                      comm=MPI.COMM_WORLD)
        else:
            self.nxs_file = h5py.File(filename, 'w')
