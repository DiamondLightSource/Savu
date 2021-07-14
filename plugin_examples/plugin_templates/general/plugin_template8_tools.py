from savu.plugins.plugin_tools import PluginTools

class PluginTemplate8Tools(PluginTools):
    """
    A plugin template that dynamically determines the number of output
    datasets based on the number of entries in the out_datasets parameter list.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None
        """