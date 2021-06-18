from savu.plugins.plugin_tools import PluginTools

class RingRemovalNormalizationTools(PluginTools):
    """Normalization-based method working in the sinogram space to remove ring
    artifacts.
    """
    def define_parameters(self):
        """
        radius:
            visibility: basic
            dtype: int
            description: Radius of the Gaussian kernel.
            default: 11
        number_of_chunks:
            visibility: basic
            dtype: int
            description:  Divide the sinogram to many chunks of rows
            default: 1
        """

