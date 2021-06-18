from savu.plugins.plugin_tools import PluginTools

class NxstxmLoaderTools(PluginTools):
    """A class to load tomography data from an NXstxm file.
    """
    def define_parameters(self):
        """
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: stxm
        """
