from savu.plugins.plugin_tools import PluginTools

class ReductionAmaxTools(PluginTools):
    """A plugin to reduce data by one dimension by taking amax along the chosen dimension.
    """
    def define_parameters(self):
        """
        axis_label:
            visibility: basic
            dtype: [str, None]
            description: Axis label name associated with the dimension to sum.
            default: label
        pattern:
             visibility: basic
             dtype: str
             options: [VOLUME_XZ, VOLUME_YZ, VOLUME_XY]
             description: Pattern to apply this to.
             default: VOLUME_XZ
        """
