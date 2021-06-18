from savu.plugins.plugin_tools import PluginTools

class SimpleFitXrfTools(PluginTools):
    """This plugin fits XRF peaks.
    """
    def define_parameters(self):
        """
        width_guess:
            visibility: intermediate
            dtype: float
            description: An initial guess at the width.
            default: 0.02
        """
