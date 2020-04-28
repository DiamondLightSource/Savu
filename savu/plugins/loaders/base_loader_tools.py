from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
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
        data_file:
              visibility: hidden
              dtype: str
              description: hidden parameter for savu template
              default: :"<>"
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