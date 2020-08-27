from savu.plugins.plugin_tools import PluginTools

class BasePtychoTools(PluginTools):
    """A base plugin for doing ptychography. Other ptychography plugins should
inherit from this.
    """
    def define_parameters(self):
        """
        in_datasets:
              visibility: datasets
              dtype: list
              description: Create a list of the dataset(s) to process
              default: []
        out_datasets:
              visibility: datasets
              dtype: list
              description: Create a list of the dataset(s) to create
              default: "['probe', 'object_transmission', 'positions']"

        """