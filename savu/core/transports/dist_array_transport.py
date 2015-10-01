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
import os
import logging
import sys

import h5py
import numpy as np

from savu.data.TransportMechanism import TransportMechanism
from savu.core.utils import logfunction
import savu.plugins.utils as pu
from savu.data.structures import RawTimeseriesData, ProjectionData, VolumeData
from savu.plugins.timeseries_field_corrections \
    import TimeseriesFieldCorrections

from contextlib import closing
from distarray.globalapi import Context, Distribution
from distarray.globalapi.distarray import DistArray as da

import savu.data.transports.dist_array_utils as du


class DistArrayTransport(TransportMechanism):

    def transport_control_setup(self, options):
        options["mpi"] = False
        options["process"] = 0
        options["processes"] = options["process_names"].split(',')
        self.set_logger_single(options)

    def set_logger_single(self, options):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(options["out_path"],
                                              'log.txt'), mode='w')
        fh.setFormatter(logging.Formatter('L %(relativeCreated)12d M CPU0 0' +
                                          ' %(levelname)-6s %(message)s'))
        logger.addHandler(fh)
        logging.info("Starting the reconstruction pipeline process")

    @logfunction
    def transport_run_plugin_list(self, exp):
        """Runs a chain of plugins
        """

        #*** temporary data file handler: Quick fix
        data_file_handler = pu.load_raw_data(input_file)
        data_file_handler.rotation_angle = \
            data_file_handler.rotation_angle[data_file_handler.image_key == 0]
            #*** moved this from timeseries_field_correction (not currently
            #done for hdf5_transport)

        logging.debug("processing Plugins")

        with closing(Context()) as context:
            targets = context.targets

        previous_plugin = None
        out_data = None
        with closing(Context(targets=targets)) as context:

            plugin = pu.load_plugin(plugin_list.plugin_list[0]['id'])
            in_data = self.load_data(context, input_file, plugin)

            for plugin_dict in plugin_list.plugin_list:

                logging.debug("Loading plugin %s", plugin_dict['id'])
                plugin = pu.load_plugin(plugin_dict['id'])
                plugin.set_parameters(plugin_dict['data'])

                [in_data, out_data] = self.create_data_object(
                    context, in_data, out_data, previous_plugin, plugin)
                # TODO
                #out_data = plugin.get_output_data(in_data)

                logging.debug("Starting processing  plugin %s",
                              plugin_dict['id'])
                plugin.run_plugin(in_data, out_data, processes, process,
                                  data_file_handler, self)
                logging.debug("Completed processing plugin %s",
                              plugin_dict['id'])

                in_data = out_data
                previous_plugin = plugin

        group_name = "process_complete"
        self.output_data(data_file_handler, in_data, plugin_list,
                         processing_dir, group_name)

    def load_data(self, context, input_file, plugin):
        ''' Create a distarray from the specified section of the HDF5 file. '''

        in_data = pu.load_raw_data(input_file)

        dist = plugin.input_dist()
        data_key = 'entry1/tomo_entry/instrument/detector/data'
        image_key = 'entry1/tomo_entry/instrument/detector/image_key'

        with h5py.File(input_file, 'r') as f:
            dataset = f[data_key]
            array_shape = dataset.shape
            in_data.image_key = f[image_key][:]

        distribution = Distribution(context, array_shape, dist=dist)
        in_data.data = context.load_hdf5(input_file, distribution=distribution,
                                         key=data_key)

        return in_data

    def output_data(self, data_file_handler, in_data, plugin_list,
                    processing_dir, group_name):
#        output_filename = self.output_plugin_list(data_file_handler, in_data,
#                    plugin_list, processing_dir)
        self.create_output_file(in_data, plugin_list, processing_dir,
                                group_name)
#        plugin_list.add_intermediate_data_link(output_filename, in_data,
#                                group_name)

    def output_plugin_list(self, data_file_handler, in_data, plugin_list,
                           processing_dir):
        import time
        filename = os.path.basename(data_file_handler.backing_file.filename)
        filename = os.path.splitext(filename)[0]
        output_filename = \
            os.path.join(processing_dir, "%s_processed_%s.nxs" %
                         (filename, time.strftime("%Y%m%d%H%M%S")))

        logging.debug("Running process List.save_list_to_file")
        plugin_list.save_list_to_file(output_filename)
        return output_filename

    def create_output_file(self, in_data, plugin_list, processing_dir,
                           group_name):

        temp = plugin_list.plugin_list
        final_plugin = temp[len(temp)-1]['id']
        file_name = \
            os.path.join(processing_dir, "%s_%s.h5" %
                        (plugin_list.name, final_plugin))
        logging.debug("Creating output file %s", file_name)
        in_data.data.context.save_hdf5(file_name, in_data.data, group_name,
                                       mode='w')

    def create_data_object(self, context, in_data, out_data, previous_plugin,
                           plugin):
        """Creates an output file of the appropriate type for a specified
            plugin

        :param data_type: Input or output data type for the current plugin
        :type plugin: str
        :returns:  The output data object
        """

        data_type = plugin.output_data_type()

        if data_type == RawTimeseriesData:
            out_data = RawTimeseriesData()
        elif data_type == ProjectionData:
            out_data = ProjectionData()
        elif data_type == VolumeData:
            out_data = VolumeData()
        else:
            print "data type undefined in " \
                  "data.transport.distArray.create_data_object()"
            sys.exit(1)

        [in_data, out_data] = self.distribute_array(
            in_data, out_data, previous_plugin, plugin)
        return [in_data, out_data]

    def distribute_array(self, in_data, out_data, previous_plugin, plugin,
                         dist=None):

        context = in_data.data.context

        if previous_plugin is not None:
            if previous_plugin.output_dist() is not plugin.input_dist():
                temp = in_data.data.toarray()
                #*** temporarily creating ndarray - read directly from the olds
                # distarray (create empty dist array and populate?)
                dist = Distribution(context, in_data.get_data_shape(),
                                    plugin.input_dist())
                in_data.data = context.fromarray(temp, plugin.output_dist())

        # ***************** temporary quick fixes *****************************
        if isinstance(out_data, VolumeData):
            shape = (in_data.data.shape[2], in_data.data.shape[1],
                     in_data.data.shape[2])
            out_data.shape = shape
        else:
            shape = in_data.data.shape
            #*** temporary fix

        if isinstance(plugin, TimeseriesFieldCorrections):
            shape = ((shape[0] -
                     len(in_data.image_key[in_data.image_key != 0])),
                     shape[1], shape[2])

        # ***************** temporary quick fixes *****************************

        print ("***creating output_distribution with shape:", shape)
        dist = Distribution(context, shape, plugin.input_dist())
        print type(out_data.data)
        out_data.data = context.zeros(dist, dtype=np.int32)
        print "***output distribution created"

        # *** temporarily copying the data and setting the shape
        out_data.rotation_angle = in_data.rotation_angle
        out_data.image_key = in_data.image_key

        return [in_data, out_data]

    def process(self, plugin, in_data, out_data, processes, process, params,
                kernel):

        if kernel is "timeseries_correction_set_up":
            kernel = du.timeseries_correction_set_up
        elif kernel is "reconstruction_set_up":
            kernel = du.reconstruction_set_up
        elif kernel is "filter_set_up":
            kernel = du.filter_set_up
        else:
            print("The kernel", kernel, "has not been registered in "
                  " dist_array_transport")
            sys.exit(1)

        iters_key = du.distributed_process(plugin, in_data, out_data,
                                           processes, process, params, kernel)

        out_data.data = da.from_localarrays(iters_key[0],
                                            context=in_data.data.context,
                                            dtype=np.int32)

    def setup(self, path, name):
        return

    def add_data_block(self, name, shape, dtype):
        self.group.create_dataset(name, shape, dtype)

    def get_data_block(self, name):
        return self.group[name]

    def finalise(self):
        if self.backing_file is not None:
            self.backing_file.close()
            self.backing_file = None


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
