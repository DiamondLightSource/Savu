from savu.plugins.plugin_tools import PluginTools

class MedianFilterTools(PluginTools):
    """A plugin to filter each frame with a 3x3 median filter.
    """
    def define_parameters(self):
        """
        kernel_size:
             visibility: basic
             dtype: tuple
             description: Kernel size for the filter.
             default: (1, 3, 3)

        pattern:
             visibility: advanced
             dtype: str
             description: Pattern to apply this to.
             default: PROJECTION

        """