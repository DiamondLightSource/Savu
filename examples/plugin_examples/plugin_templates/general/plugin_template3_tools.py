from savu.plugins.plugin_tools import PluginTools

class PluginTemplate3Tools(PluginTools):
    """
    A plugin template that reduces the data dimensions, e.g. azimuthal
    integration.
    """

    def define_parameters(self):
        """
        num_bins:
            visibility: basic
            dtype: int
            description: Length of the new dimension
            default: 10
        """