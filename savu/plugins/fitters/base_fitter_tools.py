from savu.plugins.plugin_tools import PluginTools

class BaseFitterTools(PluginTools):
    """This plugin fits peaks.
    """
    def define_parameters(self):
        """

        out_datasets:
            default: ["FitWeights", "FitWidths", "FitAreas", "residuals"]

        width_guess:
            visibility: basic
            dtype: float
            description: An initial guess at the width.
            default: 0.02

        peak_shape:
            visibility: intermediate
            dtype: str
            description: Which shape do you want.
            default: 'gaussian'

        PeakIndex:
           visibility: basic
           dtype: [list[],list]
           description: The peak index.
           default: []

        """
