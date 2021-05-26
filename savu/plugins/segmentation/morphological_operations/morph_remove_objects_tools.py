from savu.plugins.plugin_tools import PluginTools

class MorphRemoveObjectsTools(PluginTools):
    """A Plugin to remove objects smaller than the specified size.
    """
    def define_parameters(self):
        """
        min_size:
            visibility: basic
            dtype: int
            description: The smallest allowable object size.
            default: 64

        connectivity:
            visibility: basic
            dtype: int
            description: The connectivity defining the neighborhood of a pixel.
            default: 1

        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_XZ'

        """