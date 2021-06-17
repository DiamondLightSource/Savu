from savu.plugins.plugin_tools import PluginTools

class ReproduceFitTools(PluginTools):
    """This plugin reproduces the fitted curves. Its for diagnostics.
    """
    def define_parameters(self):
        """
        in_datasets:
            visibility: datasets
            dtype: list[str]
            description: Create a list of the input dataset(s)
            default: ["FitWeights", "FitWidths", "FitAreas","Backgrounds"]

        out_datasets:
            visibility: datasets
            dtype: list[str]
            description: Create a list of the output dataset(s)
            default: ["Sum", "Individual_curves"]


        """
