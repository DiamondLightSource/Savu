from savu.plugins.plugin_tools import PluginTools

class BaseAbsorptionCorrectionTools(PluginTools):
    """A base absorption correction for stxm and xrd
    """
    def define_parameters(self):
        """
        azimuthal_offset:
              visibility: basic
              dtype: float
              description: Angle between detectors.
              default: -90.0
        density:
              visibility: intermediate
              dtype: float
              description: The density
              default: 3.5377
        compound:
              visibility: intermediate
              dtype: str
              description: The compound
              default: 'Co0.1Re0.01Ti0.05(SiO2)0.84'
        """