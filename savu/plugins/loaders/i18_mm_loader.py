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
.. module:: mm_loader
   :platform: Unix
   :synopsis: A class for loading multiple data types in a multi-modal
       experimental setup.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
from savu.plugins.base_loader import BaseLoader
from savu.plugins.loaders.multi_modal_loaders.base_i18_multi_modal_loader \
    import BaseI18MultiModalLoader
from savu.plugins.loaders.multi_modal_loaders.i18_loaders import *
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18xrd_loader \
    import I18xrdLoader as xrd
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18fluo_loader \
    import I18fluoLoader as fluo
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18stxm_loader \
    import I18stxmLoader as stxm
from savu.plugins.loaders.multi_modal_loaders.i18_loaders.i18monitor_loader \
    import I18monitorLoader as mon

from savu.plugins.utils import register_plugin
from savu.core.utils import docstring_parameter


@register_plugin
class I18mmLoader(BaseLoader):
    """ Class to load multi-modal data. """

    def __init__(self, name='I18mmLoader'):
        super(I18mmLoader, self).__init__(name)
        base = BaseI18MultiModalLoader()
        base._populate_default_parameters()
        self.doc_string = base.__doc__
        self.dict = base.parameters
        self.fluo_keys = self.set_params(fluo(), 'fluo')
        self.xrd_keys = self.set_params(xrd(), 'xrd')
        self.stxm_keys = self.set_params(stxm(), 'stxm')
        self.mon_keys = self.set_params(mon(), 'monitor')
        for key, value in self.dict.iteritems():
            self.parameters[key] = value

    def set_params(self, inst, name):
        inst._populate_default_parameters()
        copy_keys = inst.parameters.viewkeys() - self.dict.viewkeys()
        for key in copy_keys:
            self.parameters[key] = inst.parameters[key]
        return list(copy_keys)

    def separate_params(self, keys):
        all_keys = self.dict.keys() + keys
        new_dict = {}
        for key in all_keys:
            new_dict[key] = self.parameters[key]
        return new_dict

    @docstring_parameter(BaseI18MultiModalLoader.__doc__, xrd.__doc__,
                         stxm.__doc__, mon.__doc__, fluo.__doc__)
    def _override_class_docstring(self):
        """ {0} \n {1} \n {2} \n {3} \n {4} """
        pass

    def setup(self):
        self._data_loader(fluo(), 'fluo', self.fluo_keys)
        self._data_loader(xrd(), 'xrd', self.xrd_keys)
        self._data_loader(stxm(), 'stxm', self.stxm_keys)
        self._data_loader(mon(), 'monitor', self.mon_keys)

    def _data_loader(self, inst, name, key):
        debug_str = 'This file contains an ' + name
        warn_str = 'This file does not contain a ' + name
        try:
            self.setup_loader(inst, self.separate_params(key))
            logging.debug(debug_str)
        except:
            logging.warn(warn_str)

    def setup_loader(self, loader, params):
        loader._main_setup(self.exp, params)
        loader.setup()
