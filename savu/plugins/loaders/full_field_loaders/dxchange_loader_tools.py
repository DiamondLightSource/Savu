from savu.plugins.plugin_tools import PluginTools

class DxchangeLoaderTools(PluginTools):
    """A class to load tomography data from a hdf5 file
    """
    def define_parameters(self):
        """
        data_path:
            visibility: basic
            dtype: h5path
            description: Path to the data.
            default: 'exchange/data'
        dark:
            visibility: basic
            dtype: list[h5path, float]
            description: Hdf path to the dark-field data and scale.
            default: ['exchange/data_dark', 1.0]
        flat:
            visibility: basic
            dtype: list[h5path, float]
            description: Hdf path to the flat-field data and scale.
            default: "['exchange/data_white', 1.0]"
        angles:
            visibility: basic
            dtype: h5path
            description: Hdf path to the angle data.
            default: 'exchange/theta'
        image_key_path:
            visibility: hidden
            dtype: None
            description: Not required.
            default: None
        """
