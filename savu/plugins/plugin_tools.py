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
from savu.data.plugin_list import CitationInformation

class MainPlugin(object):
    """ Set the class variable
    """
    def __init__(self, cls):
        self.cls = cls
        self.tool_list = self._find_tools()

    def _find_tools(self):
        """Using the method resolution order, find base class tools
        """
        tool_list = []
        for clazz in self.cls.__class__.__mro__[::-1]:
            plugin_tools_id = clazz.__module__ + '_tools'
            p_tools = pu.get_tools_class(plugin_tools_id)
            if p_tools:
                tool_list.append(p_tools)
        return tool_list

class PluginParameters(MainPlugin):
    """ Save the parameters for the plugin and base classes to a
    dictionary. The parameters are in yaml format inside the
    define_parameter function. These are read and checked for problems.
    """
    def __init__(self, cls):
        super(PluginParameters, self).__init__(cls)
        self.param = MetaData(ordered=True)
        self._populate_parameters(self.cls)

    def _populate_parameters(self, cls):
        """ Set the plugin parameters for each of the tools classes
        """
        map(lambda tool_class: self._set_plugin_parameters(tool_class), self.tool_list)

    def _set_plugin_parameters(self, clazz):
        """ Load the parameters for each base class, c, check the
        dataset visibility, check data types, set dictionary values.
        """
        all_params = self._load_param_from_doc(clazz)
        if all_params:
            # Check if the required keys are included
            self._check_required_keys(all_params, clazz)
            # Check that the dataset visibility is set
            self._check_visibility(all_params, clazz)
            # Check that the visibility levels are valid
            self._check_dtype(all_params, clazz)
            # Use a display option to apply to dependent parameters later.
            self._set_display(all_params)
            for p_name, p_value in all_params.items():
                self.param.set(p_name, p_value)

    def _load_param_from_doc(self, clazz):
        """Find the parameter information from the method docstring.
        This is provided in a yaml format.
        """
        all_params = None
        if hasattr(clazz, 'define_parameters'):
            yaml_text = clazz.define_parameters.__doc__
            if yaml_text is not None:
                all_params = doc.load_yaml_doc(yaml_text)
                if not isinstance(all_params, OrderedDict):
                    print('The parameters have not been read in correctly for',
                          clazz.__name__,'.')
        return all_params

    def modify(self, parameters, value, param_name):
        """ Check the new parameter value is valid, modify the parameter
        value, update defaults, check if dependent parameters should
        be made visible or hidden.
        """
        # This is accessed from outside this class
        if self._is_valid(value, param_name):
            value = self.check_for_default(value, param_name, parameters,
                                           self.param.get_dictionary())
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

    def check_for_default(self, value, param_name, parameters, all_params):
        """ If the value is changed to be 'default', then set the original
        default value. If the default contains a dictionary, then search
        for the correct value
        """
        if value == 'default':
            default = all_params[param_name]['default']
            if isinstance(default, OrderedDict):
                desc = all_params[param_name]['description']
                parent_param = default.keys()[0] if default.keys() else ''
                if parent_param:
                    dep_param_choices = {k: v
                                         for k, v
                                         in default[parent_param].items()}
                    # Find current parent value
                    parent_value = parameters[parent_param]
                    for item in dep_param_choices.keys():
                        if parent_value == item:
                            desc['range'] = 'The recommended value with the ' \
                                            'chosen', parent_param, 'would be', \
                                            dep_param_choices[item]
                            value = dep_param_choices[item]
            else:
                value = all_params[param_name]['default']
        return value

    def _is_valid(self, value, subelem):
        """ Check if the value provided is the same type as the type
        specified in the yaml file.
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
                    print('Your input for the parameter \'', subelem,
                          '\' must match the type ', type_options, '.',
                          Fore.RESET, sep = '')
                    print()

                else:
                    print('Your input for the parameter \'', subelem,
                          '\' must match the type ', dtype, '.',
                          Fore.RESET, sep = '')

        else:
            print('Not in parameter keys.')
        return parameter_valid

    def _check_required_keys(self, all_params, clazz):
        """ Check the four keys ['dtype', 'description', 'visibility',
        'default'] are included inside the dictionary given for each
        parameter.
        """
        required_keys = ['dtype', 'description', 'visibility', 'default']
        missing_keys = False
        missing_key_dict = {}

        for p_key, p in all_params.items():
            all_keys = p.keys()
            if p.get('visibility') == 'hidden':
                # For hidden keys, only require a default value key
                required_keys = ['default']

            if not all(d in all_keys for d in required_keys):
                missing_key_dict[p_key] = set(required_keys) - set(all_keys)
                missing_keys = True

        if missing_keys:
            print(clazz.__name__,
                  'doesn\'t contain all of the required keys.')
            for param, missing_values in missing_key_dict.items():
                print('The missing required keys for \'', param, '\' are:',
                      sep = '')
                print(*missing_values, sep=', ')

            raise Exception('Please edit %s' % clazz.__name__)

    def _check_dtype(self, all_params, clazz):
        """
        Make sure that the dtype input is valid
        """
        dtype_valid = True
        for p_key, p in all_params.items():
            if isinstance(p['dtype'], list):
                for item in p['dtype']:
                    if item not in param_u.type_dict:
                        print('The ', p_key, ' parameter has been assigned '
                             'an invalid type \'', item, '\'.', sep = '')
            else:
                if p['dtype'] not in param_u.type_dict:
                    print('The ', p_key, ' parameter has been assigned an '
                          'invalid type \'', p['dtype'], '\'.', sep = '')
                    dtype_valid = False
        if not dtype_valid:
            print('The type options are: ')
            type_list = ['    {0}'.format(key)
                         for key in param_u.type_dict.keys()]
            print(*type_list, sep='\n')
            raise Exception('Please edit %s' % clazz.__name__)

    def _check_visibility(self, all_params, clazz):
        """Make sure that the visibility choice is valid
        """
        visibility_levels = ['basic', 'intermediate', 'advanced',
                             'datasets', 'hidden']
        visibility_valid = True
        for p_key, p in all_params.items():
            self._check_data_keys(p_key, p)
            # Check that the data types are valid choices
            if p['visibility'] not in visibility_levels:
                print('Inside ', clazz.__name__, ' the ', p_key, ' parameter '
                      'is assigned an invalid visibility level \'',
                       p['visibility'], '\'')
                print('Valid choices are:')
                print(*visibility_levels, sep=', ')
                visibility_valid = False

        if not visibility_valid:
            raise Exception('Please change the file for %s' % clazz.__name__)

    def _check_data_keys(self, p_key, p):
        """ Make sure that the visibility of dataset parameters is 'datasets'
        so that the display order is unchanged.
        """
        datasets = ['in_datasets', 'out_datasets']
        if p_key in datasets:
            if p['visibility'] != 'datasets':
                p['visibility'] = 'datasets'

    def _check_options(self, all_params, clazz):
        """ Make sure that option verbose descriptions match the actual
        options
        """
        for p_key, p in all_params.items():
            desc = all_params[p_key]['description']
            if desc.get('options'):
                # TODO Make sure that option verbose descriptions match
                #  the actual options
                pass

    def _set_display(self, all_params):
        """ Initially, set all of the parameters to display 'on'
        This is later altered when dependent parameters need to be shown
        or hidden
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
                    # If there was no modification, on load, find the
                    # parent default
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
                            # If there was no modification, on loading the
                            # plugin set the correct default value
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


class PluginCitations(MainPlugin):
    """ Get this citation dictionary so get_dictionary of the metadata type
        should return a dictionary of all the citation info as taken from
        docstring
        """
    def __init__(self, cls):
        super(PluginCitations, self).__init__(cls)
        self.cite = MetaData(ordered=True)
        self.set_cite(self.cls)

    def set_cite(self, cls):
        """ Set the citations for each of the tools classes
        Change to list() for python 3
        """
        map(lambda tool_class: self._set_plugin_citations(tool_class), self.tool_list)

    def _set_plugin_citations(self, clazz):
        """ Load the parameters for each base class and set values"""
        citations = self._load_cite_from_doc(clazz)
        if citations:
            for citation in citations.values():
                new_citation = CitationInformation()
                for k, v in citation.items():
                    setattr(new_citation, k, v)
                new_citation.name = self._set_citation_name(new_citation)
                self.cite.set(new_citation.name, new_citation)

    def _citation_keys_valid(self):
        # TODO Check that required citation keys are present
        pass

    def _set_citation_name(self, new_citation):
        """ Create a short identifier using the short name of the article
        and the first author
        """
        if hasattr(new_citation, 'endnote') \
                and hasattr(new_citation, 'short_name_article'):
            cite_name = new_citation.short_name_article.title() + ' by ' \
                        + self._get_first_author(new_citation) + ' et al.'
        elif hasattr(new_citation, 'endnote'):
            cite_name = self._get_title(new_citation) + ' by ' \
                        + self._get_first_author(new_citation) + ' et al.'
        else:
            cite_name = new_citation.description
        return cite_name

    def _get_first_author(self, new_citation):
        """ Retrieve the first author name from the endnote """
        seperation_word = '%A'
        endnote = new_citation.endnote
        first_author = endnote.partition(seperation_word)[2].split('\n')[0]
        return first_author

    def _get_title(self, new_citation):
        """ Retrieve the title from the endnote """
        seperation_word = '%T'
        endnote = new_citation.endnote
        first_author = endnote.partition(seperation_word)[2].split('\n')[0]
        return first_author

    def _load_cite_from_doc(self, clazz):
        """Find the citation information from the method docstring.
        This is provided in a yaml format.
        """
        all_c = None
        if hasattr(clazz, 'get_citation'):
            yaml_text = clazz.get_citation.__doc__
            if yaml_text is not None:
                all_c = doc.load_yaml_doc(yaml_text)
                if not isinstance(all_c, OrderedDict):
                    print('The citation information has not been read in '
                          'correctly for', clazz.__name__,'.')
        return all_c


class PluginDocumentation(MainPlugin):
    """ Get this documentation dictionary so get_dictionary of
    the metadata type should return a dictionary of all the
    documentation details taken from docstring
    """
    def __init__(self, cls):
        super(PluginDocumentation, self).__init__(cls)
        self.doc = MetaData()
        self.set_doc()

    def set_doc(self):
        self.doc.set('verbose', self.__doc__)
        self.doc.set('warn', self.config_warn.__doc__)

    def config_warn(self):
        pass

class PluginTools(PluginParameters, PluginCitations, PluginDocumentation):
    """Holds all of the parameter, citation and documentation information
    for one plugin class - cls"""

    def __init__(self, cls):
        super(PluginTools, self).__init__(cls)
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
