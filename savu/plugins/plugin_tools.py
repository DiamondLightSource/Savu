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


class PluginParameters(object):
    """ Save the parameters for the plugin and base classes to a
    dictionary. The parameters are in yaml format inside the
    define_parameter function. These are read and checked for problems.
    """
    def __init__(self):
        super(PluginParameters, self).__init__()
        self.param = MetaData(ordered=True)

    def populate_parameters(self, tools_list):
        """ Set the plugin parameters for each of the tools classes
        """
        map(lambda tool_class: self._set_plugin_parameters(tool_class),
            tools_list)

    def _set_plugin_parameters(self, tool_class):
        """ Load the parameters for each base class, c, check the
        dataset visibility, check data types, set dictionary values.
        """
        all_params = self._load_param_from_doc(tool_class)
        if all_params:
            # Check if the required keys are included
            self._check_required_keys(all_params, tool_class)
            # Check that option values are valid
            self._check_options(all_params, tool_class)
            # Check that the dataset visibility is set
            self._check_visibility(all_params, tool_class)
            # Check that the visibility levels are valid
            self._check_dtype(all_params, tool_class)
            # Use a display option to apply to dependent parameters later.
            self._set_display(all_params)
            for p_name, p_value in all_params.items():
                self.param.set(p_name, p_value)

    def _load_param_from_doc(self, tool_class):
        """Find the parameter information from the method docstring.
        This is provided in a yaml format.
        """
        all_params = None
        if hasattr(tool_class, 'define_parameters'):
            yaml_text = tool_class.define_parameters.__doc__
            if yaml_text is not None:
                all_params = doc.load_yaml_doc(yaml_text)
                if not isinstance(all_params, OrderedDict):
                    print('The parameters have not been read in correctly '
                          'for', tool_class.__name__, '.')
        return all_params

    def modify(self, parameters, value, param_name):
        """ Check the parameter is within the current parameter list.
        Check the new parameter value is valid, modify the parameter
        value, update defaults, check if dependent parameters should
        be made visible or hidden.
        """
        # This is accessed from outside this class

        parameter_valid = False
        current_parameter_details = self.param.get(param_name)
        # If found, then the parameter is within the current parameter list
        # displayed to the user
        if current_parameter_details:
            parameter_valid = param_u.is_valid(param_name, value,
                                               current_parameter_details)
            # Check that the value is an accepted input for the chosen parameter
            if parameter_valid:
                value = self.check_for_default(value, param_name, parameters,
                                               self.param.get_dictionary())
                parameters[param_name] = value
                self.update_defaults(parameters, self.param.get_dictionary(),
                                     mod=param_name)
                # Update the list of parameters to hide those dependent on others
                self.check_dependencies(parameters, self.param.get_dictionary())
                parameter_valid = True
            else:
                print('This value has not been saved as it was not'
                      ' a valid entry.')
        else:
            print('Not in parameter keys.')

        return parameter_valid

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


    def _check_required_keys(self, all_params, tool_class):
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
            print(tool_class.__name__,
                  'doesn\'t contain all of the required keys.')
            for param, missing_values in missing_key_dict.items():
                print('The missing required keys for \'', param, '\' are:',
                      sep='')
                print(*missing_values, sep=', ')

            raise Exception('Please edit %s' % tool_class.__name__)

    def _check_dtype(self, all_params, tool_class):
        """
        Make sure that the dtype input is valid
        """
        dtype_valid = True
        for p_key, p in all_params.items():
            if isinstance(p['dtype'], list):
                for item in p['dtype']:
                    if item not in param_u.type_dict:
                        print('The ', p_key, ' parameter has been assigned '
                                             'an invalid type \'', item, '\'.', sep='')
            else:
                if p['dtype'] not in param_u.type_dict:
                    print('The ', p_key, ' parameter has been assigned an '
                                         'invalid type \'', p['dtype'], '\'.', sep='')
                    dtype_valid = False
        if not dtype_valid:
            print('The type options are: ')
            type_list = ['    {0}'.format(key)
                         for key in param_u.type_dict.keys()]
            print(*type_list, sep='\n')
            raise Exception('Please edit %s' % tool_class.__name__)

    def _check_visibility(self, all_params, tool_class):
        """Make sure that the visibility choice is valid
        """
        visibility_levels = ['basic', 'intermediate', 'advanced',
                             'datasets', 'hidden']
        visibility_valid = True
        for p_key, p in all_params.items():
            self._check_data_keys(p_key, p)
            # Check that the data types are valid choices
            if p['visibility'] not in visibility_levels:
                print('Inside ', tool_class.__name__, ' the ', p_key, ' parameter '
                                                                 'is assigned an invalid visibility level \'',
                      p['visibility'], '\'')
                print('Valid choices are:')
                print(*visibility_levels, sep=', ')
                visibility_valid = False

        if not visibility_valid:
            raise Exception('Please change the file for %s' % tool_class.__name__)

    def _check_data_keys(self, p_key, p):
        """ Make sure that the visibility of dataset parameters is 'datasets'
        so that the display order is unchanged.
        """
        datasets = ['in_datasets', 'out_datasets']
        if p_key in datasets:
            if p['visibility'] != 'datasets':
                p['visibility'] = 'datasets'

    def _check_options(self, all_params, tool_class):
        """ Make sure that option verbose descriptions match the actual
        options
        """
        options_valid = True
        for p_key, p in all_params.items():
            desc = all_params[p_key]['description']
            if isinstance(desc, dict):
                options = all_params[p_key].get('options')
                option_desc = desc.get('options')
                if options and option_desc:
                    # Check that there is not an invalid option description
                    # inside the option list.
                    invalid_option = [opt for opt in option_desc
                                      if opt not in options]
                    if invalid_option:
                        options_valid = False
                        break

        if options_valid is False:
            raise Exception('Please check the parameter options for %s'
                            % tool_class.__name__)

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
    def __init__(self):
        super(PluginCitations, self).__init__()
        self.cite = MetaData(ordered=True)

    def set_cite(self, tools_list):
        """ Set the citations for each of the tools classes
        Change to list() for Python 3
        """
        map(lambda tool_class: self._set_plugin_citations(tool_class), tools_list)

    def _set_plugin_citations(self, tool_class):
        """ Load the parameters for each base class and set values"""
        citations = self._load_cite_from_doc(tool_class)
        if citations:
            for citation in citations.values():
                new_citation = CitationInformation()
                if self._citation_keys_valid(citation, tool_class):
                    for k, v in citation.items():
                        setattr(new_citation, k, v)
                    new_citation.name = self._set_citation_name(new_citation,
                                                                tool_class)
                    self.cite.set(new_citation.name, new_citation)
                else:
                    print('The citation for', tool_class.__name__,
                          'was not saved.')

    def _citation_keys_valid(self, new_citation, tool_class):
        """ Check that required citation keys are present. Return false if
        required keys are missing
        """
        citation_keys_valid = False
        required_keys = ['description']
        # Inside the fresnel filter there is only a description
        citation_keys = [k for k in new_citation.keys()]
        # Check that all of the required keys are contained inside the
        # citation definition
        check_keys = all(item in citation_keys for item in required_keys)
        if check_keys is False:
            citation_keys_valid = False
        else:
            citation_keys_valid = True

        all_keys = ['short_name_article', 'description', 'bibtex',
                    'endnote', 'doi', 'dependency']
        # Keys which are not used
        additional_keys = [k for k in citation_keys if k not in all_keys]
        if additional_keys:
            print('Please only use the following keys inside the citation'
                  ' definition for', tool_class.__name__, ':')
            print(*all_keys, sep=", ")
            print('The incorrect keys used:', additional_keys)

        return citation_keys_valid

    def _set_citation_name(self, new_citation, tool_class):
        """ Create a short identifier using the short name of the article
        and the first author
        """
        endnote = new_citation.endnote.strip()
        # Remove blank space
        if endnote and hasattr(new_citation, 'short_name_article'):
            cite_name = new_citation.short_name_article.title() + ' by ' \
                        + self._get_first_author(new_citation) + ' et al.'
        elif endnote:
            cite_name = self._get_title(new_citation) + ' by ' \
                        + self._get_first_author(new_citation) + ' et al.'
        else:
            # Set the tools class name as the citation name
            module_name = tool_class.__module__.split('.')[-1].replace('_', ' ')
            cite_name = module_name.split('tools')[0].title()
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

    def _load_cite_from_doc(self, tool_class):
        """Find the citation information from the method docstring.
        This is provided in a yaml format.
        """
        all_c = None
        if hasattr(tool_class, 'get_citation'):
            yaml_text = tool_class.get_citation.__doc__
            if yaml_text is not None:
                all_c = doc.load_yaml_doc(yaml_text)
                if not isinstance(all_c, OrderedDict):
                    print('The citation information has not been read in '
                          'correctly for', tool_class.__name__, '.')
        return all_c

    def define_citations(self):
        pass


class PluginDocumentation(object):
    """ Get this documentation dictionary so get_dictionary of
    the metadata type should return a dictionary of all the
    documentation details taken from docstring
    """
    def __init__(self):
        super(PluginDocumentation, self).__init__()
        self.doc = MetaData()

    def set_doc(self, tools_list):
        # Use the tools class at the 'top'
        self.doc.set('verbose', tools_list[-1].__doc__)
        self.doc.set('warn', tools_list[-1].config_warn.__doc__)

    def config_warn(self):
        pass


class PluginTools(PluginParameters, PluginCitations, PluginDocumentation):
    """Holds all of the parameter, citation and documentation information
    for one plugin class - cls"""

    def __init__(self, cls):
        super(PluginTools, self).__init__()
        self.plugin_class = cls
        self.tools_list = self._find_tools()
        self._set_tools_data()

    def _find_tools(self):
        """Using the method resolution order, find base class tools"""
        tool_list = []
        for tool_class in self.plugin_class.__class__.__mro__[::-1]:
            plugin_tools_id = tool_class.__module__ + '_tools'
            p_tools = pu.get_tools_class(plugin_tools_id)
            if p_tools:
                tool_list.append(p_tools)
        return tool_list

    def _set_tools_data(self):
        """Populate the parameters, citations and documentation
        with information from all of the tools classes
        """
        self.populate_parameters(self.tools_list)
        self.set_cite(self.tools_list)
        self.set_doc(self.tools_list)

    def get_param(self):
        return self.param.get_dictionary()

    def get_citations(self):
        return self.cite.get_dictionary()

    def get_doc(self):
        return self.doc.get_dictionary()
