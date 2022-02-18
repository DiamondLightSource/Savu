from savu.plugins.plugin_tools import PluginTools


class PaddingDummyTools(PluginTools):
    """padding dummy
    """

    def define_parameters(self):
        """
        padding:
            visibility: basic
            dtype: int
            description: The amount of pixels to pad each slab.
            default: 3
        """
