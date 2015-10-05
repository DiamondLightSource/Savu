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
.. module:: meta_data
   :platform: Unix
   :synopsis: Contains the MetaData class which holds all information required
   by the pipeline throughout processing.  An instance of MetaData is held by
   the Experiment class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import savu
from copy import copy


class MetaData(object):
    """
    The MetaData class creates a dictionary of all meta data which can be
    accessed using the get and set methods. It also holds an instance of
    PluginList.
    """

    def __init__(self, options={}):
        self.dict = options.copy()

    def load_experiment_collection(self):
        transport_collection = self.dict["transport"] + "_experiment"
        class_name = ''.join(x.capitalize() for x in
                             transport_collection.split('_'))
        self.add_base(globals()[class_name])

    def add_base(self, transport):
        cls = self.__class__
        self.__class__ = cls.__class__(cls.__name__, (cls, transport), {})

    def set_meta_data(self, name, value):
        maplist = (name if type(name) is list else [name])
        self.get_meta_data(maplist[:-1], True)[maplist[-1]] = value

    def get_meta_data(self, maplist, setFlag=False):
        if not maplist:
            return self.dict
        else:
            function = lambda k, d: d[k]
            maplist = (maplist if type(maplist) is list else [maplist])
            it = iter(maplist)
            accum_value = self.dict
            for x in it:
                while True:
                    try:
                        accum_value = function(x, accum_value)
                    except KeyError:
                        if setFlag is True:
                            accum_value[x] = {}
                            continue
                        else:
                            errorStr = 'The metadata ' + str(maplist) + \
                                       ' does not exist'
                            raise KeyError(errorStr)
                    break
            return accum_value

    def copy_dictionary(self, data_obj, **kwargs):
        """ Copy keys from one dictionary to another.

        Keyword arguments:
        :param rawFlag: Indicate that the dictionary to copy contains
        information relating to raw tomography data (inherits from TomoRaw)
        :param priority_name: priority name
        :param message: message to display
        :returns: formatted string
        """

        new_dict = data_obj.meta_data.get_dictionary()
        to_remove = self.dict.keys()
        rawFlag = True if isinstance(data_obj, savu.data.data_structures.TomoRaw) else False
        copy_keys = kwargs.get(set("copyKeys"), set(new_dict.keys()))
        remove_keys = kwargs.get(set("removeKeys"), [])

        if rawFlag is True:
            to_remove = to_remove.union(["image_key"])

        to_remove = to_remove.union(remove_keys)
        copy_keys = to_remove.symmetric_difference(copy_keys)

        for key in copy_keys:
            try:
                self.dict[key] = copy(new_dict[key])
            except KeyError:
                pass

    def get_dictionary(self):
        return self.dict


class Hdf5Experiment():
    """
    The Hdf5Experiment class is inherited by Experiment class at
    runtime and performs initial setup of metadata
    """
    def set_transport_meta_data(self):
        pass


class distArrayExperiment():
    """
    The Hdf5Experiment class is inherited by Experiment class at
    runtime and performs initial setup of metadata
    """
    def set_transport_meta_data(self):
        pass
