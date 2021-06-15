from savu.plugins.plugin_tools import PluginTools

class ImageTemplateLoaderTools(PluginTools):
    """A class to load data from a folder of FabIO compatible images using data
    descriptions loaded from a yaml file.
    """
    def define_parameters(self):
        """
        yaml_file:
              visibility: basic
              dtype: [None,yamlfilepath]
              description: Path to the file containing the data descriptions.
              default: None
        """