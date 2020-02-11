from savu.data.meta_data import MetaData
import savu.plugins.docstring_parser as doc
# from dataclasses import dataclass


class PluginCitations(object):
    """ Get this citation dictionary so get_dictionary of the metadata type
        should return a dictionary of all the citation info as taken from docstring
        """
    def __init__(self):
        super(PluginCitations, self).__init__()
        self.cite_info = MetaData()
        self.cite_set()

    def cite_set(self):
        self.cite_info.set('bibtex', self.get_bibtex.__doc__)
        self.cite_info.set('endnote', self.get_endnote().__doc__)

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
        self.param_info = MetaData()
        self._get_plugin_parameters()

    def _get_plugin_parameters(self):
        # function to get plugin parameters
        params = MetaData()
        # get the docstring
        # read yaml structure
        # check the parameter
        yaml_text = self.define_parameters.__doc__
        all_params, verbose = doc._load_yaml(yaml_text)

        for key, value in params.get_dictionary().iteritems():
            name = key
            param_dict = value
            vis = all_params['vis']
            dtype = all_params['type']
            dep = all_params['dep'] if 'dep' in param_dict.keys() else None
            self.param_info.set(name, param_dict)
            #params[name] = Parameter(vis, dtype, dep)
        # create dictionary

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
            param_dict['visibility'] = self.visibility
            param_dict['type'] = self.datatype
            param_dict['description'] = self.description
            # and the rest
            return param_dict
    """
class PluginDocumentation(object):
    """ Get this documentation
     diction so get_dictionary of the metadata type
        should return a dictionary of all the parameters as taken from docstring
    """
    def __init__(self):
        super(PluginDocumentation, self).__init__()
        self.doc_info = MetaData()

class PluginInfo(PluginCitations, PluginParameters, PluginDocumentation):

    def __init__(self):
        self.plugin_info = MetaData()
        super(PluginInfo, self).__init__()
        self.plugin_info.set('citation_info', self.cite_info.get_dictionary())
        self.plugin_info.set('parameters', self.param_info.get_dictionary())
        self.plugin_info.set('documentation', self.doc_info.get_dictionary())

