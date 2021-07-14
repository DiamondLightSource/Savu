from savu.plugins.plugin_tools import PluginTools

class PluginTemplate6Tools(PluginTools):
    """
    A template to create a plugin that changes the shape of the data,
    e.g. downsample_filter.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None
        bin_size:
            visibility: basic
            dtype: int
            description: Bin size for the downsample
            default: 2
        pattern:
            visibility: basic
            dtype: str
            description: The pattern the plugin should be applied to
            default: ['PROJECTION']
        """