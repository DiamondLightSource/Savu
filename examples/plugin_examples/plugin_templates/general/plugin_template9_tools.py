from savu.plugins.plugin_tools import PluginTools

class PluginTemplate9Tools(PluginTools):
    """
    A plugin template that dynamically determines the number of output
    datasets based on a parameter.
    """

    def define_parameters(self):
        """
        n_out:
            visibility: basic
            dtype: int
            description: Add this number of output datasets
            default: 1
        out_prefix:
            visibility: basic
            dtype: [None, str]
            description: What should the datasets be called
            default: None
        """