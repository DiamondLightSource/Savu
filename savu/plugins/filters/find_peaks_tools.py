from savu.plugins.plugin_tools import PluginTools

class FindPeaksTools(PluginTools):
    """This plugin uses peakutils to find peaks in spectra. This is then metadata.

    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: 'Create a list of the dataset(s).'
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