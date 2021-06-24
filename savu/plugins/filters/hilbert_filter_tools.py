from savu.plugins.plugin_tools import PluginTools

class HilbertFilterTools(PluginTools):
    """
    A plugin to apply Hilbert filter horizontally for tomographic
    reconstruction of phase gradient images. 
    """

    def config_warn(self):
        """
        Set 'log' to False and 'FBP_filter' to None in reconstruction plugin.
        """
