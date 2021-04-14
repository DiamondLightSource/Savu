from savu.plugins.plugin_tools import PluginTools

class P2rFlyScanDetectorLoaderTools(PluginTools):
    """A class to load p2r fly scan detector data from a Nexus file.
    """
    def define_parameters(self):
        """
        data_path:
            visibility: intermediate
            dtype: str
            description: Path to the data inside the file
            default: 'entry1/tomo_entry/data/data'
        image_key_path:
            visibility: intermediate
            dtype: hdf5path
            description: Path to the image key entry inside the nxs file.
            default: 'entry1/tomo_entry/instrument/detector/image_key'
        dark:
            visibility: intermediate
            dtype: list[filepath, hdf5path, int]
            description: Optional path to the dark field data file, nxs path and\
              scale value.
            default: '[None, None, 1]'
        flat:
            visibility: intermediate
            dtype: list[filepath, hdf5path, int]
            description: Optional path to the flat field data file, nxs path and\
              scale value.
            default: '[None, None, 1]'
        angles:
            visibility: intermediate
            dtype: str
            description: A python statement to be evaluated or a file.
            default: None
        3d_to_4d:
            visibility: intermediate
            dtype: bool
            description: Set to true if this reshape is required.
            default: False
        ignore_flats:
            visibility: intermediate
            dtype: [list[int],None]
            description: List of batch numbers of flats (start at 1) to\
              ignore.
            default: None
        """
