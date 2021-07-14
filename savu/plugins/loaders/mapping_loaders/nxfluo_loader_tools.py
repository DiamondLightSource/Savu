from savu.plugins.plugin_tools import PluginTools

class NxfluoLoaderTools(PluginTools):
    """A class to load tomography data from an NXFluo file.
    """
    def define_parameters(self):
        """
        fluo_offset:
            visibility: basic
            dtype: float
            description: fluo scale offset.
            default: 0.0
        fluo_gain:
            visibility: intermediate
            dtype: float
            description: fluo gain
            default: 0.01
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: fluo

        """
