from savu.plugins.plugin_tools import PluginTools

class PyfaiAzimuthalIntegratorTools(PluginTools):
    """1D azimuthal integrator by pyFAI
    """

    def define_parameters(self):
        """
        use_mask:
            visibility: basic
            dtype: bool
            description: 'Should we mask.'
            default: False

        num_bins:
            visibility: basic
            dtype: int
            description: 'Number of bins.'
            default: 1005

        """