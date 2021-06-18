from savu.plugins.plugin_tools import PluginTools

class NxxrdLoaderTools(PluginTools):
    """A class to load tomography data from an NXxrd file.
    """
    def define_parameters(self):
        """
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: xrd
        calibration_path:
            visibility: basic
            dtype: [None,str]
            description: Path to the calibration file
            default: None
        """
