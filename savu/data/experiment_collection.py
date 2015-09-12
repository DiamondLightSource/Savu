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
.. module:: experiment_collection
   :platform: Unix
   :synopsis: Contains the Experiment class and all possible experiment 
   collections from which Experiment can inherit at run time.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import os
import time
import logging

from savu.data.plugin_list import PluginList
from savu.data.data_structures import Data
from savu.data.meta_data import MetaData

class Experiment(object):
    """
    One instance of this class is created at the beginning of the 
    processing chain and remains until the end.  It holds the current data
    object and a dictionary containing all metadata.
    """

    def __init__(self, options):
        self.meta_data = MetaData(options)
        self.meta_data_setup(options["process_file"])
        self.index = {"in_data": {}, "out_data": {}}

    def meta_data_setup(self, process_file):
        self.meta_data.load_experiment_collection()
        self.meta_data.plugin_list = PluginList()
        self.meta_data.plugin_list.populate_plugin_list(process_file)

    def create_data_object(self, dtype, name, bases=[]):
        try:
            self.index[dtype][name]
        except KeyError:
            self.index[dtype][name] = Data(name)
            data_obj = self.index[dtype][name]
            bases.append(data_obj.get_transport_data(self.meta_data.get_meta_data("transport")))
            data_obj.add_base_classes(bases)
        return self.index[dtype][name]


    def set_nxs_filename(self):
        name = self.index["in_data"].keys()[0]
        filename = os.path.basename(self.index["in_data"][name].backing_file.filename)
        filename = os.path.splitext(filename)[0]
        filename = os.path.join(self.meta_data.get_meta_data("out_path"),
                                "%s_processed_%s.nxs" % (filename,
                                time.strftime("%Y%m%d%H%M%S")))
        self.meta_data.set_meta_data("nxs_filename", filename)

    def clear_data_objects(self):
        self.index["out_data"] = {}
        self.index["in_data"] = {}

    def clear_out_data_objects(self):
        self.index["out_data"] = {}

    def set_out_data_to_in(self):
        self.index["in_data"] = self.index["out_data"]
        self.index["out_data"] = {}

    def log(self, log_tag, log_level=logging.DEBUG):
        """
        Log the contents of the experiment at the specified level
        """
        logging.log(log_level, "Experimental Parameters for %s", log_tag)
        for key, value in self.index["in_data"].iteritems():
            logging.log(log_level, "in data (%s) shape = %s", key,
                        value.get_shape())
        for key, value in self.index["in_data"].iteritems():
            logging.log(log_level, "out data (%s) shape = %s", key,
                        value.get_shape())
