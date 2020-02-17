# replaces tomobar_recon_yaml.py
from savu.plugins.plugin_tools import PluginTools

class BaseTools(PluginTools):
    """
    module: plugin
    platform: Unix
    synopsis: Base class for all plugins used by Savu
    moduleauthor: Mark Basham <scientificsoftware@diamond.ac.uk>

    """
    def define_parameters(self):
        """---
        in_datasets:
            visibility: param
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        out_datasets:
            visibility: param
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []

        """
