from savu.plugins.plugin_tools import PluginTools

class I13SpeckleLoaderTools(PluginTools):
    """A class to load tomography data from an NXstxm file
    """
    def define_parameters(self):
        """
        signal_key:
            visibility: basic
            dtype: float
            description: Path to the signals
            default: 9.1
        reference_key:
            visibility: intermediate
            dtype: h5path
            description: Path to the reference
            default: '/entry/reference'
        angle_key:
            visibility: intermediate
            dtype: h5path
            description: Path to the reference
            default: '/entry/theta'
        dataset_names:
            visibility: intermediate
            dtype: list
            description: The output sets.
            default: ['signal','reference']

        """
