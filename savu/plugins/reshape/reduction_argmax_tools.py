from savu.plugins.plugin_tools import PluginTools

class ReductionArgmaxTools(PluginTools):
    """A plugin to reduce data by one dimension by taking argmax along the dimension.
    """
    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: Explicitly state the slicing pattern.
            default: 'VOLUME_XZ'
        axis_label:
            visibility: basic
            dtype: [str, None]
            description: Axis label name assigned to the dimension to sum.
            default: label            
        """
