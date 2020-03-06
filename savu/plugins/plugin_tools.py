from savu.data.meta_data import MetaData
import savu.plugins.docstring_parser as doc
# from dataclasses import dataclass
from collections import OrderedDict


class PluginCitations(object):
    """ Get this citation dictionary so get_dictionary of the metadata type
        should return a dictionary of all the citation info as taken from
        docstring
        """
    def __init__(self):
        super(PluginCitations, self).__init__()
        self.cite = MetaData()
        self.set_cite()

    def set_cite(self):
        citation = {'bibtex': self.get_bibtex.__doc__,  'endnote': self.get_endnote.__doc__}
        self.cite.set(self.__class__.__name__, citation)

    def get_bibtex(self):
        pass

    def get_endnote(self):
        pass

class PluginParameters(object):
    """ Get this parameter dictionary so get_dictionary of the metadata type
    should return a dictionary of all the parameters as taken from docstring
    """
    def __init__(self):
        super(PluginParameters, self).__init__()
        self.param = MetaData(ordered=True)
        self.set_plugin_parameters()

    def set_plugin_parameters(self):
        # function to get plugin parameters

        yaml_text = self.define_parameters.__doc__
        all_params = doc.load_yaml_doc(yaml_text)
        if isinstance(all_params, OrderedDict):
            for p_name, p_value in all_params.items():
                self.param.set(p_name, p_value)
        else:
            print('The parameters have not been read in correctly for '
                  + str(self.__class__.__name__) + '.')

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
            # and the rest
            return param_dict
    """
class PluginDocumentation(object):
    """ Get this documentation dictionary so get_dictionary of
    the metadata type should return a dictionary of all the
    documentation details taken from docstring
    """
    def __init__(self):
        super(PluginDocumentation, self).__init__()
        self.doc = MetaData()
        self.set_doc()

    def set_doc(self):
        self.doc.set('verbose', self.__doc__)

class PluginTools(PluginCitations, PluginParameters, PluginDocumentation):

    def __init__(self, plugin_tools=MetaData()):
        self.plugin_tools = plugin_tools
        super(PluginTools, self).__init__()

        # To do - reset the plugin tools when each new plugin loaded
        if self.__class__.__name__ == 'BaseTools':
            self.plugin_tools.set('param', OrderedDict())
            self.plugin_tools.set('cite', OrderedDict())
            self.plugin_tools.set('doc', MetaData())

        self.plugin_tools.set('doc', self.doc.get_dictionary())
        self.plugin_tools.append('param', self.param.get_dictionary())
        self.plugin_tools.append('cite', self.cite.get_dictionary())

