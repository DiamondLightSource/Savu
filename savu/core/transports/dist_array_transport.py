# Copyright 2015 Diamond Light Source Ltd.
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
.. module:: HDF5
   :platform: Unix
   :synopsis: Transport for saving and loading files using hdf5

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import numpy as np

from savu.core.transport_control import TransportControl
from contextlib import closing
from distarray.globalapi import Context, Distribution
from distarray.globalapi.distarray import DistArray as da

import savu.core.transports.dist_array_utils as du
from savu.core.transport_setup import MPI_setup


class DistArrayTransport(TransportControl):

    def __init__(self):
        self.targets = None
        self.context = None
        self.n_processes = None
        self.count = None
        self.history = []

    def _transport_initialise(self, options):
        # self.exp is not available here
        MPI_setup(options)  # change this?
        with closing(Context()) as context:
            self.targets = context.targets  # set mpi logging here?

    def _transport_pre_plugin_list_run(self):
        self.n_processes = \
            self.exp.meta_data.plugin_list._get_n_processing_plugins()
        self.context = Context(targets=self.targets)
        closing(self.context).__enter__()

    def _transport_pre_plugin(self):
        # store all datasets and associated patterns
        self.__update_history(self.exp.index)
        self.__distribute_arrays(self.exp.index)

    def _transport_post_plugin(self):
        # if you wish to output datasets that have been removed from the index
        # then do that here (data.remove is True)
        pass

    def _transport_post_plugin_list_run(self):
        # convert distarrays to hdf5
        for data in self.exp.index['in_data'].values():
            name = data.get_name()
            fname = self.exp.meta_data.get('filename')[name]
            gname = self.exp.meta_data.get('group_name')[name]
            data.data.context.save_hdf5(fname, data.data, gname, mode='w')
            self.exp._get_experiment_collection()['saver_plugin']\
                ._open_read_only(data, fname, gname)
        closing(self.context).__exit__()

    def __update_history(self, data_index):
        for dtype, data_dict in data_index.iteritems():
            for name, dobj in data_dict.iteritems():
                pattern = dobj._get_plugin_data().get_pattern()
                self.history.append({name: pattern})

    def __distribute_arrays(self, data_index):
        if not self.history:
            self.__load_data_from_hdf5(data_index['in_data'])  # expand this later for other types (or first set should always be treated as hdf5 dataset?)
            # - i.e. get data as before directly from file and output to distributed array
        else:
            self.__redistribute_data(data_index['in_data'])
        self.__create_out_data(data_index['out_data'])

    def __redistribute_data(self, data_list):
        """ Calculate the pattern distributions and if they are not the same\
        redistribute.
        """
        for data in data_list.values():
            patterns = self.__get_distribution_history(data.get_name())

        if patterns[0] != patterns[1]:
            temp = data.data.toarray()
            # *** temporarily creating ndarray
            # distarray (create empty dist array and populate?)
            distribution = \
                Distribution(self.context, data.get_shape(), patterns[-1])  # currently redundant
            data.data = self.context.fromarray(temp, patterns[-1])

    def __load_data_from_hdf5(self, data_list):
        ''' Create a distarray from the specified section of the HDF5 file. '''

        for data in data_list:
            input_file = data.backing_file.filename
            dist = self.__calculate_distribution(
                data._get_plugin_data().get_pattern())
            distribution = \
                Distribution(self.context, data.get_shape(), dist=dist)
            data.data = self.context.load_hdf5(
                input_file, distribution=distribution, key=data.name)

    def __create_out_data(self, out_data):
        for data in out_data.values():
            dist = self.__calculate_distribution(
                data._get_plugin_data().get_pattern())
            dist = Distribution(self.context, data.get_shape(), dist)
            data.data = self.context.zeros(dist, dtype=np.int32)

    def __get_distribution_history(self, name):
        hist = [i for i in range(len(self.history)) if
                self.history[i].keys()[0] == name][-2:]
        return [self.__calculate_distribution(
            self.history[p].values()[0]) for p in hist]

    def __calculate_distribution(self, pattern):
        core_dirs = pattern.values()[0]['core_dir']
        slice_dirs = pattern.values()[0]['slice_dir']
        nDims = len(core_dirs + slice_dirs)
        dist = ['n']*nDims
        for sl in slice_dirs:
            dist[sl] = 'b'
        return ''.join(dist)
