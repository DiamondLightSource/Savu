from savu.plugins.plugin_tools import PluginTools

class PluginTemplate7Tools(PluginTools):
    """
    A plugin template that increases the data dimensions.
    """

    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: PROJECTION
        axis_len:
            visibility: basic
            dtype: int
            description: Length of the new dimension
            default: 10
        axis_label:
            visibility: basic
            dtype: str
            description: Axis label for the new axis
            default: scan
        axis_unit:
            visibility: basic
            dtype: str
            description: Axis unit for the new axis
            default: number
        """