from savu.plugins.plugin_tools import PluginTools

class YamlConverterTools(PluginTools):
    """A class to load data from a non-standard nexus/hdf5 file using
    descriptions loaded from a yaml file.
    """
    def define_parameters(self):
        """
        yaml_file:
              visibility: basic
              dtype: [None,yamlfilepath]
              description: Path to the file containing the data descriptions.
              default: None
        template_param:
              visibility: hidden
              dtype: [str,dict]
              description: A hidden parameter to hold parameters passed in
                via a savu template file.
              default: {}
        """