from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class BaseAstraReconTools(PluginTools):
    """A Plugin to perform Astra toolbox reconstruction
    """
    def define_parameters(self):
        """---
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of Iterations - only valid for iterative algorithms
            default: 1

        """