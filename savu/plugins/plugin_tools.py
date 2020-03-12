from colorama import Fore
from collections import OrderedDict

import savu.plugins.utils as pu
from savu.data.meta_data import MetaData
import savu.plugins.docstring_parser as doc

class PluginParameters(object):
    """ Get this parameter dictionary so get_dictionary of the metadata type
    should return a dictionary of all the parameters as taken from docstring
    """
    def __init__(self, **kwargs):
        super(PluginParameters, self).__init__()
        self.param = MetaData(ordered=True)
        self.populate_parameters(kwargs['cls'])

    def populate_parameters(self, cls):
        for clazz in cls.__class__.__mro__[::-1]:
            p_tools = self.get_plugin_tools(clazz)
            if p_tools:
                self.set_plugin_parameters(p_tools)

    def set_plugin_parameters(self, clazz):
        all_params = self.load_parameters(clazz)
        self.check_required_keys(all_params, clazz)
        self.set_values(all_params)
        for p_name, p_value in all_params.items():
            self.param.set(p_name, p_value)

    def get_plugin_tools(self, clazz):
        tool_class = None
        plugin_tools_id = clazz.__module__ + '_tools'
        if plugin_tools_id == 'savu.plugins.plugin_tools':
            plugin_tools_id = 'savu.plugins.base_tools'
        if pu.load_tools.get(plugin_tools_id):
            tool_class = pu.load_tools[plugin_tools_id]
        return tool_class

    def load_parameters(self, clazz):
        yaml_text = clazz.define_parameters.__doc__
        all_params = doc.load_yaml_doc(yaml_text)
        if not isinstance(all_params, OrderedDict):
            print('The parameters have not been read in correctly for '
                  + str(clazz.__name__) + '.')
        return all_params

    def check_required_keys(self, all_params, clazz):
        required_keys = ['dtype', 'description', 'visibility', 'default']
        for p_key, p in all_params.items():
            all_keys = p.keys()
            if p.get('visibility') == 'hidden':
                required_keys = ['default']

            if not all(d in all_keys for d in required_keys):
                print('Loading '+str(self.__class__.__name__))
                print(str(clazz.__name__)
                      + ' doesn\'t contain all of the required parameters.')
                print('The missing required keys for ' + str(p_key)
                      + ' are: ')
                print(', '.join(set(required_keys) - set(all_keys)))

    def set_values(self, all_params):
        for k, v in all_params.items():
            v['current_value'] = v['default']

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
    def __init__(self, **kwargs):
        super(PluginCitations, self).__init__()
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


class PluginTools(PluginParameters, PluginCitations, PluginDocumentation):

    def __init__(self, **kwargs):
        super(PluginTools, self).__init__(**kwargs)
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
