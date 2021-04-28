from savu.plugins.plugin_tools import PluginTools

class RingRemovalInterpolationTools(PluginTools):
    """Method to remove stripe artefacts in a sinogram (<-> ring artefacts
in a reconstructed image) using a combination of a detection technique
and an interpolation technique.
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

