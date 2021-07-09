from savu.plugins.plugin_tools import PluginTools

class PluginTemplate1Tools(PluginTools):
    """
    A simple plugin template with one in_dataset and one out_dataset with 
    similar characteristics, e.g. median filter.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: int
            description: Example of a plugin parameter
            default: 1
        """
