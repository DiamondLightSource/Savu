from savu.plugins.plugin_tools import PluginTools

class BaseFitterTools(PluginTools):
    """This plugin fits peaks.
    """
    def define_parameters(self):
        """
        in_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: Create a list of the dataset(s)
            default: []

        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: Create a list of the dataset(s)
            default: ["FitWeights", "FitWidths", "FitAreas", "residuals"]

        width_guess:
            visibility: intermediate
            dtype: float
            description: An initial guess at the width.
            default: 0.02

        peak_shape:
            visibility: intermediate
            dtype: str
            description: Which shape do you want.
            default: 'gaussian'

        PeakIndex:
           visibility: intermediate
           dtype: [list[],list]
           description: The peak index.
           default: []

        """
