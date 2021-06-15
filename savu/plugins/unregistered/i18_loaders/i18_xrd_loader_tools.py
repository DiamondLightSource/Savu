from savu.plugins.plugin_tools import PluginTools

class I18XrdLoaderTools(PluginTools):
    """A class to load tomography data from an xrd file
    """
    def define_parameters(self):
        """
        data_path:
            visibility: basic
            dtype: [None,str]
            description: Path to the folder containing the data.
            default: None
        calibration_path:
            visibility: basic
            dtype: [None,h5path]
            description: path to the calibration file.
            default: None
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'xrd'

        """
