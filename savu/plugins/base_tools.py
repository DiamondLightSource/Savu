from savu.plugins.plugin_tools import PluginTools

class BaseTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """
        in_datasets:
            visibility: basic
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        out_datasets:
            visibility: basic
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []

        """
