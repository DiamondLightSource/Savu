from savu.plugins.plugin_tools import PluginTools

class IcaTools(PluginTools):
    """This plugin performs independent component analysis on XRD/XRF spectra.
    """
    def define_parameters(self):
        """
        w_init:
             visibility: basic
             dtype: list
             description: The initial mixing matrix.
             default: None

        random_state:
             visibility: intermediate
             dtype: int
             description: The state
             default: 1

        """

