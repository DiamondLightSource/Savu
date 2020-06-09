from savu.plugins.plugin_tools import PluginTools

class DownsampleFilterTools(PluginTools):
    """A plugin to reduce the data in the selected dimension by a proportion.
    """
    def define_parameters(self):
        """
        bin_size:
            visibility: basic
            dtype: list
            description: Bin Size for the downsample.
            default: 2
        mode:
            visibility: basic
            dtype: int
            description: One of 'mean', 'median', 'min', 'max'.
            default: 'mean'
        pattern:
            visibility: basic
            dtype: int
            description:  One of 'PROJECTION' or 'SINOGRAM'.
            default: PROJECTION

        """

