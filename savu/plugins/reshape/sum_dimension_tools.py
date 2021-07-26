from savu.plugins.plugin_tools import PluginTools

class SumDimensionTools(PluginTools):
    """
    Sum over a dimension of the data.
    """

    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: [str, None]
            description: How to slice the data passed to the plugin
            default: None
        axis_label:
            visibility: basic
            dtype: [str, None]
            description: Axis label name assigned to the dimension to sum.
            default: None
        """
