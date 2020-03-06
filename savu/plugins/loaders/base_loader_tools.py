from savu.plugins.plugin_tools import PluginTools

class BaseLoaderTools(PluginTools):
    """A base class for loader plugins. A base plugin from which all data loader plugins should inherit.
    """
    def define_parameters(self):
        """---
        preview:
              visibility: basic
              dtype: '[int]'
              description: A slice list of required frames.
              default: []
        in_datasets:
              visibility: hidden
              dtype: list
              description: Create a list of the dataset(s) to process
              default: []
        out_datasets:
              visibility: hidden
              dtype: list
              description: Create a list of the dataset(s) to create
              default: []

        """