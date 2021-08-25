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
   :synopsis: Contains the MetaData class which holds all information \
   required by the pipeline throughout processing.  An instance of MetaData \
   is held by the Experiment class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import copy
import logging
from collections import OrderedDict


class MetaData(object):
    """
    The MetaData class creates a dictionary of all meta data which can be \
    accessed using the get and set methods. It also holds an instance of \
    PluginList.
    """

    def __init__(self, options={}, ordered=False):
        self.dict = OrderedDict(options) if ordered else options.copy()

    def set(self, name, value):
        """ Create and set an entry in the meta data dictionary.

        :param name: dictionary key(s). If ``name`` is a list then each
            successive name will become an entry in the dictionary which has
            the previous name as its key.
        :type name: str or list(str)
        :param value value: dictionary value

        For example,

            >>> MetaDataObj.set(['name1', 'name2'], 3)
            >>> MetaDataObj.get_dictionary()
            {'name1': {'name2': 3}}
        """
        maplist = name if isinstance(name, list) else [name]
        self.get(maplist[:-1], True)[maplist[-1]] = value

    def get(self, maplist, setFlag=False, value=True, units=False):
        """ Get a value from the meta data dictionary, given its key(s).

        :params maplist: Dictionary key(s).
        :type maplist: str or list(str)
        :returns: Value from the dictionary corresponding to the given key(s)
        :rtype: value

        Dictionaries within dictionaries are accessed by placing successive
        keys in a list.
        """
        if not maplist:
            return self.dict

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

        if isinstance(accum_value, dict) and accum_value:
            options = OrderedDict([('value', value), ('units', units)])
            if not set(accum_value.keys()).difference(set(options.keys())):
                accum_value = [accum_value[k] for k, v in options.items()
                               if v is True]
        return accum_value

    def delete(self, entry):
        """ Delete an entry from the meta data dictionary.

        :param str entry: The dictionary key entry to delete.
        """
        try:
            del self.get_dictionary()[entry]
        except KeyError:
            logging.warning("Trying to delete a dictionary entry that doesn't "
                         "exist.")

    def get_dictionary(self):
        """ Get the meta_data dictionary.

        :returns: A dictionary.
        :rtype: dict
        """
        return self.dict

    def _set_dictionary(self, ddict):
        """ Set the meta data dictionary """
        self.dict = copy.deepcopy(ddict)

    def __getitem__(self, key):
        return self.dict[key]