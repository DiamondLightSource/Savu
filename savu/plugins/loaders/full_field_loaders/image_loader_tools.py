from savu.plugins.plugin_tools import PluginTools

class ImageLoaderTools(PluginTools):
    """Load any FabIO compatible formats (e.g. tiffs)
    """
    def define_parameters(self):
        """
        dataset_name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        angles:
            visibility: intermediate
            dtype: [None, str, int]
            description: 'A python statement to be evaluated
              (e.g np.linspace(0, 180, nAngles)) or a file.'
            default: None
        frame_dim:
            visibility: intermediate
            dtype: [None,int]
            description: Which dimension requires stitching?
            default: None
        data_prefix:
            visibility: intermediate
            dtype: [None,str]
            description: A file prefix for the data file.
            default: None
        dark_prefix:
            visibility: intermediate
            dtype: [None,str]
            description: A file prefix for the dark field files, including the
              folder path if different from the data.
            default: None
        flat_prefix:
            visibility: intermediate
            dtype: [None,str]
            description: A file prefix for the flat field files, including the
              folder path if different from the data.
            default: None

        """
