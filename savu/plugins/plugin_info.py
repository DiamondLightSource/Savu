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
        self.cite_info.set('endnote', self.get_endnote.__doc__)

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
        self.param_info = self.get_plugin_parameters()

    def get_plugin_parameters(self):
        # function to get plugin parameters
        params = MetaData()
        yaml_text = self.define_parameters.__doc__
        all_params, verbose = doc.load_yaml_doc(yaml_text)
        for p_name, p_value in all_params.items():
            params.set(p_name, p_value)
            vis = p_value['visibility']
            dtype = p_value['dtype']
            dep = p_value['dependency'] if 'dependency' in all_params.keys() else None
            #params[p_name] = Parameter(vis, dtype, dep)
        return params

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
        self.doc_set()

    def doc_set(self):
        self.doc_info.set('doc', self.__doc__)

class PluginInfo(PluginCitations, PluginParameters, PluginDocumentation):

    def __init__(self):
        self.plugin_info = MetaData()
        super(PluginInfo, self).__init__()
        self.plugin_info.set('citation_info', self.cite_info.get_dictionary())
        self.plugin_info.set('parameters', self.param_info.get_dictionary())
        self.plugin_info.set('documentation', self.doc_info.get_dictionary())

