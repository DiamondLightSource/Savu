from savu.plugins.plugin_tools import PluginTools

class NxmonitorLoaderTools(PluginTools):
    """A class to load tomography data from an NXmonitor file
    """
    def define_parameters(self):
        """
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: monitor
        """
