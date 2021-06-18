from savu.plugins.plugin_tools import PluginTools

class SpectrumCropTools(PluginTools):
    """Crops a spectrum to a range
    """
    def define_parameters(self):
        """
        crop_range:
              visibility: intermediate
              dtype: list
              description: Range to crop to.
              default: [2., 18.]
        axis:
              visibility: intermediate
              dtype: str
              description: Axis.
              default: energy

        """