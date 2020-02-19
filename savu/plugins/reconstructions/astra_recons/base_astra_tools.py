from savu.plugins.plugin_tools import PluginTools

class BaseAstraTools(PluginTools):
    """A Plugin to perform Astra toolbox reconstruction
    """
    def define_parameters(self):
        """---
        n_iterations:
            visibility: user
            dtype: int
            description: Number of Iterations - only valid for iterative algorithms
            default: 1

        """