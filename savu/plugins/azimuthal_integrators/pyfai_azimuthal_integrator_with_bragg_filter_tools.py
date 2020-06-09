from savu.plugins.plugin_tools import PluginTools

class PyfaiAzimuthalIntegratorWithBraggFilterTools(PluginTools):
    """Uses pyfai to remap the data. We then remap, percentile file and integrate.
    """
    def define_parameters(self):
        """
        use_mask:
              visibility: basic
              dtype: bool
              description: Should we mask.
              default: False

        num_bins:
              visibility: basic
              dtype: int
              description: Number of bins.
              default: 1005

        num_bins_azim:
              visibility: intermediate
              dtype: int
              description: Number of azimuthal bins.
              default: 200
        thresh:
              visibility: intermediate
              dtype: list
              description: Threshold of the percentile filter
              default: '[5,95]'

        """