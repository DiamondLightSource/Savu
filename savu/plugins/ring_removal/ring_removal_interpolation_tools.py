from savu.plugins.plugin_tools import PluginTools

class RingRemovalInterpolationTools(PluginTools):
    """Interpolation-based method working in the sinogram space to remove ring
    artifacts.
    """
    def define_parameters(self):
        """
        size:
            visibility: basic
            dtype: [float, list[float]]
            description: Size of the median filter window. Greater is stronger.
            default: 31
        snr:
            visibility: basic
            dtype: float
            description: Ratio used to locate stripe artifacts. Greater is
              less sensitive.
            default: 3.0
        """

