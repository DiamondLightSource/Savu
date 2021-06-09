from savu.plugins.plugin_tools import PluginTools

class MorphProcLineTools(PluginTools):
    """A Larix morphological processing module using line segments to remove
inconsistent gaps
    """
    def define_parameters(self):
        """
        primeclass:
            visibility: basic
            dtype: int
            description: a mask class to start morphological processing from.
            default: 0

        correction_window:
            visibility: intermediate
            dtype: int
            description: the size of the correction window.
            default: 7

        iterations:
            visibility: basic
            dtype: int
            description: the number of iterations for segmentation.
            default: 15

        pattern:
            visibility: basic
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_YZ'

        """
