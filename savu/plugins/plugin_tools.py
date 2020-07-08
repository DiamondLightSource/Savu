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
.. module:: plugin_tools
   :platform: Unix
   :synopsis: Plugin tools

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

from __future__ import print_function, division, absolute_import

from colorama import Fore
from collections import OrderedDict

import savu.plugins.utils as pu
from savu.data.meta_data import MetaData
import savu.plugins.docstring_parser as doc
import savu.plugins.parameter_utils as param_u

class PluginParameters(object):
    """ Get this parameter dictionary so get_dictionary of the metadata
    type should return a dictionary of all the parameters as taken
    from docstring
    """
    def __init__(self, cls, **kwargs):
        super(PluginParameters, self).__init__(**kwargs)
        self.param = MetaData(ordered=True)
        self._populate_parameters(cls)

    def _populate_parameters(self, cls):
        """ Using method resolution order, find base class tools
        """
        for clazz in cls.__class__.__mro__[::-1]:
            plugin_tools_id = clazz.__module__ + '_tools'
            p_tools = pu.get_tools_class(plugin_tools_id)
            if p_tools:
                self._set_plugin_parameters(p_tools)

    def _set_plugin_parameters(self, clazz):
        """ Load the parameters for each base class and set values"""
        all_params = self._load_param_from_doc(clazz)
        if all_params:
            self._check_required_keys(all_params, clazz)
            self._check_data_keys(all_params)
            self._check_dtype(all_params, clazz)
            self._set_display(all_params)
            for p_name, p_value in all_params.items():
                self.param.set(p_name, p_value)

    def _load_param_from_doc(self, clazz):
        """Find the parameter information from the method docstring.
        This is provided in a yaml format.
        """
        all_params = None
        yaml_text = clazz.define_parameters.__doc__
        if yaml_text is not None:
            all_params = doc.load_yaml_doc(yaml_text)
            if not isinstance(all_params, OrderedDict):
                print('The parameters have not been read in correctly for '
                      + str(clazz.__name__) + '.')
        return all_params

    def modify(self, parameters, value, param_name):
        """
        Check the new parameter value is valid, modify the parameter
        value, update defaults, check if dependent parameters should
        be made visible or hidden
        """
        # This is accessed from outside this class
        if self._is_valid(value, param_name):
            parameters[param_name] = value
            self.update_defaults(parameters, self.param.get_dictionary(),
                                 mod=param_name)
            # Update the list of parameters to hide those dependent on others
            self.check_dependencies(parameters, self.param.get_dictionary())
            return True
        else:
            print('This value has not been saved as it was not'
                  ' a valid entry.')
            return False

    def _is_valid(self, value, subelem):
        """
        Check if the value provided is the same type as the type specified
        in the yaml file.
        """
        parameter_valid = False
        if self.param.get(subelem):
            # The parameter is within the current shown parameter list
            p = self.param.get(subelem)
            dtype = p['dtype']
            default_value = p['default']
            parameter_valid = param_u.is_valid(dtype, p, value, default_value)
            if parameter_valid is False:
                if isinstance(dtype, list):
                    type_options = ' or '.join([str(t) for t in dtype])
                    print('Your input for the parameter \'%s\' must match the'
                          ' type %s.' % (subelem, type_options) + Fore.RESET)
                    print()

                else:
                    print('Your input for the parameter \'%s\' must match the'
                      ' type %s' % (subelem, dtype) + Fore.RESET)

        else:
            print('Not in parameter keys.')
        return parameter_valid

    def _check_required_keys(self, all_params, clazz):
        """
        Check there are four keys ['dtype', 'description', 'visibility', 'default']
        inside the dictionary given for each parameter
        """
        required_keys = ['dtype', 'description', 'visibility', 'default']
        for p_key, p in all_params.items():
            all_keys = p.keys()
            if p.get('visibility') == 'hidden':
                # For hidden keys, only require a default value key
                required_keys = ['default']

            if not all(d in all_keys for d in required_keys):
                print('Loading '+str(self.__class__.__name__))
                print(str(clazz.__name__)
                      + ' doesn\'t contain all of the required parameters.')
                print('The missing required keys for ' + str(p_key)
                      + ' are: ')
                print(', '.join(set(required_keys) - set(all_keys)))

    def _check_data_keys(self, all_params):
        """
        Make sure that the visibility of dataset parameters is 'datasets'
        so that the display order is unchanged
        """
        datasets = ['in_datasets', 'out_datasets']
        for p_key, p in all_params.items():
            if p_key in datasets:
                if p['visibility'] != 'datasets':
                    p['visibility'] = 'datasets'

    def _check_dtype(self, all_params, clazz):
        """
        Make sure that the dtype input is valid
        """
        for p_key, p in all_params.items():
            if isinstance(p['dtype'], list):
                for item in p['dtype']:
                    if item not in param_u.type_dict:
                        print('Inside %s the %s parameter is assigned an invalid type'
                              ' \'%s\'' % (clazz.__name__, p_key, item))
            else:
                if p['dtype'] not in param_u.type_dict:
                    print('Inside %s the %s parameter is assigned an invalid type'
                          ' \'%s\'' % (clazz.__name__, p_key, p['dtype']))
                    print('The type options are: ')
                    for key in param_u.type_dict.keys():
                        print('     ' + str(key))

    def _check_options(self, all_params, clazz):
        """
        Make sure that option verbose descriptions match the actual options
        """
        for p_key, p in all_params.items():
            desc = all_params[p_key]['description']
            if desc.get('options'):
                pass

    def _set_display(self, all_params):
        """
        Initially, set all of the parameters to display 'on'
        This is later altered for dependent parameters to be shown and hidden
        """
        for k, v in all_params.items():
            v['display'] = 'on'

    def update_defaults(self, parameters, all_params, mod=False):
        """ Check if the default field of each parameter holds a dictionary.
        If it does, then check the default parameter keys to find the default
        value of the given parameter
        """
        default_list = {k: v['default'] for k, v in all_params.items()
                        if isinstance(v['default'], OrderedDict)}
        for p_name, default in default_list.items():
            desc = all_params[p_name]['description']
            parent_param = default.keys()[0] if default.keys() else ''

            if parent_param:
                dep_param_choices = {k: v
                                     for k, v in default[parent_param].items()}
                if mod:
                    # If there was a modification, find current parent value
                    parent_value = parameters[parent_param]
                else:
                    # If there was no modification, on load, find the parent default
                    parent_value = all_params[parent_param]['default']
                for item in dep_param_choices.keys():
                    if parent_value == item:
                        desc['range'] = 'The recommended value with the chosen ' \
                                        + str(parent_param) + ' would be ' \
                                        + str(dep_param_choices[item])
                        recommendation = 'It\'s recommended that you update ' \
                                         + str(p_name) + ' to ' \
                                         + str(dep_param_choices[item])
                        if mod:
                            if mod == parent_param:
                                print(Fore.RED + recommendation + Fore.RESET)
                        else:
                            # If there was no modification, on loading the plugin set
                            # the correct default value
                            parameters[p_name] = dep_param_choices[item]

    def check_dependencies(self, parameters, all_params):
        """ Determine which parameter values are dependent on a parent
        value and whether they should be hidden or shown
        """
        dep_list = {k: v['dependency']
                    for k, v in all_params.items() if 'dependency' in v}
        for p_name, dependency in dep_list.items():
            if isinstance(dependency, OrderedDict):
                parent_param_name = dependency.keys()[0]
                parent_choice_list = dependency[parent_param_name]
                # The choices which must be in the parent value

                if parent_param_name in parameters:
                    ''' Check that the parameter is in the current plug in
                    This is relevant for base classes which have several
                    dependent classes
                    '''
                    parent_value = parameters[parent_param_name]

                    if parent_value in parent_choice_list:
                        if all_params[p_name].get('display') == 'off':
                            all_params[p_name]['display'] = 'on'
                    else:
                        if all_params[p_name].get('display') != 'off':
                            all_params[p_name]['display'] = 'off'


    def define_parameters(self):
        pass

    def config_warn(self):
        pass

    """
    @dataclass
    class Parameter:
        ''' Descriptor of Parameter Information for plugins
        '''
        visibility: int
        datatype: specific_type
        description: str
        default: int
        Options: Optional[[str]]
        dependency: Optional[]

        def _get_param(self):
            param_dict = {}
            param_dict['visibility'] = self.visibility
            param_dict['type'] = self.dtype
            param_dict['description'] = self.description
            # and the remaining keys
            return param_dict
    """


class PluginCitations(object):
    """ Get this citation dictionary so get_dictionary of the metadata type
        should return a dictionary of all the citation info as taken from
        docstring
        """
    def __init__(self, **kwargs):
        super(PluginCitations, self).__init__(**kwargs)
        self.cite = MetaData()
        self.set_cite()

    def set_cite(self):
        citation = {'bibtex': self.get_bibtex.__doc__,
                    'endnote': self.get_endnote.__doc__}
        self.cite.set(self.__class__.__name__, citation)
        # To do - Save the citation for mro

    def get_bibtex(self):
        pass

    def get_endnote(self):
        pass


class PluginDocumentation(object):
    """ Get this documentation dictionary so get_dictionary of
    the metadata type should return a dictionary of all the
    documentation details taken from docstring
    """
    def __init__(self, **kwargs):
        super(PluginDocumentation, self).__init__()
        self.doc = MetaData()
        self.set_doc()

    def set_doc(self):
        self.doc.set('verbose', self.__doc__)
        self.doc.set('warn', self.config_warn.__doc__)


class PluginTools(PluginParameters, PluginCitations, PluginDocumentation):

    def __init__(self, cls, **kwargs):
        super(PluginTools, self).__init__(cls=cls, **kwargs)
        self.plugin_tools = MetaData()
        self.plugin_tools.set('param', self.param.get_dictionary())
        self.plugin_tools.set('cite', self.cite.get_dictionary())
        self.plugin_tools.set('doc', self.doc.get_dictionary())

    def get_param(self):
        return self.plugin_tools.get('param')

    def get_citations(self):
        return self.plugin_tools.get('cite')

    def get_doc(self):
        return self.plugin_tools.get('doc')
