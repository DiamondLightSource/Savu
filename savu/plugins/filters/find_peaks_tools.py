from savu.plugins.plugin_tools import PluginTools

class FindPeaksTools(PluginTools):
    """This plugin uses peakutils to find peaks in spectra and add them to
    the metadata.
    """

    def define_parameters(self):
        """
        out_datasets:
              default: ['Peaks']
        thresh:
              visibility: basic
              dtype: float
              description: Threshold for peak detection
              default: 0.03
        min_distance:
              visibility: basic
              dtype: int
              description: Minimum distance for peak detection.
              default: 15
        """