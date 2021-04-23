from savu.plugins.plugin_tools import PluginTools

class XrdAbsorptionApproximationTools(PluginTools):
    """
    McNears absorption correction, takes in a normalised absorption sinogram
    and xrd sinogram stack. A base absorption correction for stxm and xrd.
    """

    def define_parameters(self):
        """
        azimuthal_offset:
              visibility: intermediate
              dtype: int
              description: angle between detectors.
              default: 0
        density:
              visibility: basic
              dtype: float
              description: The density
              default:  3.5377
        compound:
              visibility: basic
              dtype: str
              description: The compound
              default: 'Co0.2(Al2O3)0.8'
        log_me:
              visibility: intermediate
              dtype: bool
              description: should we log the transmission.
              default: True

        """