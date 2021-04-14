from savu.plugins.plugin_tools import PluginTools

class PyfaiAzimuthalIntegratorWithBraggFilterTools(PluginTools):
    """
    Uses pyfai to remap the data. We then remap, percentile file and
    integrate.
    """
    
    def define_parameters(self):
        """
        num_bins_azim:
              visibility: basic
              dtype: int
              description: Number of azimuthal bins.
              default: 200
        thresh:
              visibility: intermediate
              dtype: list[float,float]
              description: Threshold of the percentile filter
              default: [5, 95]
    
        """