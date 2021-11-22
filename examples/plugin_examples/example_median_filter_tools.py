from savu.plugins.plugin_tools import PluginTools

class ExampleMedianFilterTools(PluginTools):
    """
    A plugin to filter each frame with a 3x3 median filter
    """

    def define_parameters(self):
        """
        kernel_size:
            visibility: basic
            dtype: list[int]
            description: Kernel size for the filter.
            default:  [1, 3, 3]
        """