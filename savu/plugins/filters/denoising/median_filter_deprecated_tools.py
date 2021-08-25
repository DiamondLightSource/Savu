from savu.plugins.plugin_tools import PluginTools

class MedianFilterDeprecatedTools(PluginTools):
    """A plugin to filter each frame with a 3x3 median filter
    """

    def define_parameters(self):
        """
        kernel_size:
             visibility: basic
             dtype: list[int]
             description: Kernel size of the median filter.
             default: [1, 3, 3]
        pattern:
             visibility: intermediate
             dtype: str
             description: Pattern to apply this to.
             default: PROJECTION

        """