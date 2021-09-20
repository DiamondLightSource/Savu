from savu.plugins.plugin_tools import PluginTools

class DezingerSinogramGpuTools(PluginTools):
    """A GPU plugin to apply median-based dezinger to SINOGRAM data. \
    The plugin works in 2D or 3D mode.
    """
    def define_parameters(self):
        """
        """