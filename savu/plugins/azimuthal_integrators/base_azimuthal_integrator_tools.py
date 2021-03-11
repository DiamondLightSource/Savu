from savu.plugins.plugin_tools import PluginTools

class BaseAzimuthalIntegratorTools(PluginTools):
    """A base azimuthal integrator for pyfai
    """
    def define_parameters(self):
        """
        use_mask:
            visibility: basic
            dtype: bool
            description: Option to apply a mask.
            default: False

        num_bins:
            visibility: basic
            dtype: int
            description: Number of bins.
            default: 1005

        """