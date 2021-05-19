from savu.plugins.plugin_tools import PluginTools

class SimpleFitTools(PluginTools):
    """This plugin fits peaks.
    """
    def define_parameters(self):
        """
        width_guess:
            visibility: basic
            dtype: float
            description: An initial guess at the width.
            default: 0.02

        PeakIndex:
            visibility: basic
            dtype: [list[],list]
            description: The peak index
            default: []

        """
