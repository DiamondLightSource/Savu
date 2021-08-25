from savu.plugins.plugin_tools import PluginTools

class ImageLoaderTools(PluginTools):
    """Load tomographic data in image format (tiff)
    """
    def define_parameters(self):
        """
        data_prefix:
            visibility: basic
            dtype: [None,str]
            description: A file prefix for the data file.
            default: None
        dark_prefix:
            visibility: basic
            dtype: [None,str]
            description: A file prefix for the dark field files, including the
              folder path if different from the data.
            default: None
        flat_prefix:
            visibility: basic
            dtype: [None,str]
            description: A file prefix for the flat field files, including the
              folder path if different from the data.
            default: None
        angles:
            visibility: basic
            dtype: [None, str, int]
            description: 'A python statement to be evaluated
              (e.g np.linspace(0, 180, nAngles)) or a file.'
            default: None
        frame_dim:
            visibility: intermediate
            dtype: int
            description: Axis (dimension) for stacking 2D images
            default: 0
        dataset_name:
            visibility: intermediate
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        """
