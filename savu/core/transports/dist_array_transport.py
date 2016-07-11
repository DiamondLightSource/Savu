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

    def _transport_post_plugin_list_run(self):
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
#
#
#    def __load_data(self, data):
#        ''' Create a distarray from the specified section of the HDF5 file. '''
#        if data.data is 
#
#        # get initial Data objects
#        in_data = self.exp.index['in_data']
#        # load the start dataset(s) here (self.load_data())
#
#        for data in in_data:
#            dist = self.calculate_distribution()
#
#            distribution = Distribution(self.context, array_shape, dist=dist)
#            in_data.data = self.context.load_hdf5(
#                input_file, distribution=distribution, key=data_key) # path to the data in the hdf5 file (get this from data.data)
#
#



#    def _transport_process(self, plugin, in_data, out_data, processes,
#                           process, params, kernel):
#
#        iters_key = du.distributed_process(plugin, in_data, out_data,
#                                           processes, process, params, kernel)
#
#        out_data.data = da.from_localarrays(iters_key[0],
#                                            context=in_data.data.context,
#                                            dtype=np.int32)
#
#    def setup(self, path, name):
#        return
#
#    def add_data_block(self, name, shape, dtype):
#        self.group.create_dataset(name, shape, dtype)
#
#    def get_data_block(self, name):
#        return self.group[name]
#
#    def finalise(self):
#        if self.backing_file is not None:
#            self.backing_file.close()
#            self.backing_file = None


#class DistArrayTransport(TransportMechanism):
#
#    @logfunction
#    def run_plugin_list(self, input_file, plugin_list, processing_dir,
#                        processes=["CPU0"], process=0):
#        """Runs a chain of plugins
#
#        :param input_file: The input file name.
#        :type input_file: str.
#        :param plugin_list: Plugin list.
#        :type plugin_list: savu.data.structure.PluginList.
#        :param processing_dir: Location of the processing directory.
#        :type processing_dir: str.
#        :param mpi: Whether this is running in mpi, default is false.
#        :type mpi: bool.
#        """
#
#        data_file_handler = pu.load_raw_data(input_file)
#        #*** temporary data file handler: Quick fix
#        data_file_handler.rotation_angle = \
#            data_file_handler.rotation_angle[data_file_handler.image_key == 0]
#            #*** moved this from timeseries_field_correction (not currently
#            # done for hdf5_transport)
#
#        logging.debug("processing Plugins")
#
#        with closing(Context()) as context:
#            targets = context.targets
#
#        previous_plugin = None
#        out_data = None
#        with closing(Context(targets=targets)) as context:
#
#            plugin = pu.load_plugin(plugin_list.plugin_list[0]['id'])
#            in_data = self.load_data(context, input_file, plugin)
#
#            for plugin_dict in plugin_list.plugin_list:
#
#                logging.debug("Loading plugin %s", plugin_dict['id'])
#                plugin = pu.load_plugin(plugin_dict['id'])
#                plugin.set_parameters(plugin_dict['data'])
#
#                [in_data, out_data] = self.create_data_object(context, in_data,
#                                                              out_data,
#                                                              previous_plugin,
#                                                              plugin)
#                # TODO
#                #out_data = plugin.get_output_data(in_data)
#
#                logging.debug("Starting processing  plugin %s",
#                              plugin_dict['id'])
#                plugin.run_plugin(in_data, out_data, processes,
#                                  process, data_file_handler, self)
#                logging.debug("Completed processing plugin %s",
#                              plugin_dict['id'])
#
#                in_data = out_data
#                previous_plugin = plugin
#
#        group_name = "process_complete"
#        self.output_data(data_file_handler, in_data, plugin_list,
#                         processing_dir, group_name)
#
#    def load_data(self, context, input_file, plugin):
#        ''' Create a distarray from the specified section of the HDF5 file. '''
#
#        in_data = pu.load_raw_data(input_file)
#
#        dist = plugin.input_dist()
#        data_key = 'entry1/tomo_entry/instrument/detector/data'
#        image_key = 'entry1/tomo_entry/instrument/detector/image_key'
#
#        with h5py.File(input_file, 'r') as f:
#            dataset = f[data_key]
#            array_shape = dataset.shape
#            in_data.image_key = f[image_key][:]
#
#        distribution = Distribution(context, array_shape, dist=dist)
#        in_data.data = context.load_hdf5(input_file, distribution=distribution,
#                                         key=data_key)
#
#        return in_data
#
#    def output_data(self, data_file_handler, in_data, plugin_list,
#                    processing_dir, group_name):
#        #output_filename = self.output_plugin_list(data_file_handler, in_data,
#                    #plugin_list, processing_dir)
#        self.create_output_file(in_data, plugin_list, processing_dir,
#                                group_name)
#        #plugin_list.add_intermediate_data_link(output_filename, in_data,
#                                #group_name)
#
#    def output_plugin_list(self, data_file_handler, in_data, plugin_list,
#                           processing_dir):
#        import time
#        filename = os.path.basename(data_file_handler.backing_file.filename)
#        filename = os.path.splitext(filename)[0]
#        output_filename = \
#            os.path.join(processing_dir, "%s_processed_%s.nxs" %
#                         (filename, time.strftime("%Y%m%d%H%M%S")))
#
#        logging.debug("Running process List.save_list_to_file")
#        plugin_list.save_list_to_file(output_filename)
#        return output_filename
#
#    def create_output_file(self, in_data, plugin_list, processing_dir,
#                           group_name):
#
#        temp = plugin_list.plugin_list
#        final_plugin = temp[len(temp)-1]['id']
#        file_name = os.path.join(processing_dir, "%s_%s.h5" %
#                                 (plugin_list.name, final_plugin))
#        logging.debug("Creating output file %s", file_name)
#        in_data.data.context.save_hdf5(file_name, in_data.data, group_name,
#                                       mode='w')
#
#    def create_data_object(self, context, in_data, out_data, previous_plugin,
#                           plugin):
#        """Creates an output file of the appropriate type for a specified
#            plugin
#
#        :param data_type: Input or output data type for the current plugin
#        :type plugin: str
#        :returns:  The output data object
#        """
#
#        data_type = plugin.output_data_type()
#
#        if data_type == RawTimeseriesData:
#            out_data = RawTimeseriesData()
#        elif data_type == ProjectionData:
#            out_data = ProjectionData()
#        elif data_type == VolumeData:
#            out_data = VolumeData()
#        else:
#            print "data type undefined in "\
#                  " data.transport.distArray.create_data_object()"
#            sys.exit(1)
#
#        [in_data, out_data] = self.distribute_array(in_data, out_data,
#                                                    previous_plugin, plugin)
#        return [in_data, out_data]
#
#    def distribute_array(self, in_data, out_data, previous_plugin, plugin,
#                         dist=None):
#
#        context = in_data.data.context
#
#        if previous_plugin is not None:
#            if previous_plugin.output_dist() is not plugin.input_dist():
#                temp = in_data.data.toarray()
#                #*** temporarily creating ndarray - read directly from the old
#                # distarray (create empty dist array and populate?)
#                dist = Distribution(context, in_data.get_data_shape(),
#                                    plugin.input_dist())
#                in_data.data = context.fromarray(temp, plugin.output_dist())
#
#        # ***************** temporary quick fixes *****************************
#        if isinstance(out_data, VolumeData):
#            shape = (in_data.data.shape[2], in_data.data.shape[1],
#                     in_data.data.shape[2])
#            out_data.shape = shape
#        else:
#            shape = in_data.data.shape
#            #*** temporary fix
#
#        if isinstance(plugin, TimeseriesFieldCorrections):
#            shape = ((shape[0] -
#                     len(in_data.image_key[in_data.image_key != 0])),
#                     shape[1], shape[2])
#
#        # ***************** temporary quick fixes *****************************
#
#        print ("***creating output_distribution with shape:", shape)
#        dist = Distribution(context, shape, plugin.input_dist())
#        print type(out_data.data)
#        out_data.data = context.zeros(dist, dtype=np.int32)
#        print "***output distribution created"
#
#        # *** temporarily copying the data and setting the shape
#        out_data.rotation_angle = in_data.rotation_angle
#        out_data.image_key = in_data.image_key
#
#        return [in_data, out_data]
#
#    def process(self, plugin, in_data, out_data, processes, process, params,
#                kernel):
#
#        if kernel is "timeseries_correction_set_up":
#            kernel = du.timeseries_correction_set_up
#        elif kernel is "reconstruction_set_up":
#            kernel = du.reconstruction_set_up
#        elif kernel is "filter_set_up":
#            kernel = du.filter_set_up
#        else:
#            print("The kernel", kernel, "has not been registered in "
#                  " dist_array_transport")
#            sys.exit(1)
#
#        iters_key = du.distributed_process(plugin, in_data, out_data,
#                                           processes, process, params, kernel)
#
#        out_data.data = da.from_localarrays(iters_key[0],
#                                            context=in_data.data.context,
#                                            dtype=np.int32)
#
#    def setup(self, path, name):
#        return
#
#    def add_data_block(self, name, shape, dtype):
#        self.group.create_dataset(name, shape, dtype)
#
#    def get_data_block(self, name):
#        return self.group[name]
#
#    def finalise(self):
#        if self.backing_file is not None:
#            self.backing_file.close()
#            self.backing_file = None
