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


class MetaData(object):
    """
    The MetaData class creates a dictionary of all meta data which can be \
    accessed using the get and set methods. It also holds an instance of \
    PluginList.
    """

    def __init__(self, options=None):
        if options is None:
            options = {}
        self.dict = options.copy()

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

    def get_dictionary(self):
        return self.dict

    def set_dictionary(self, ddict):
        self.dict = ddict
