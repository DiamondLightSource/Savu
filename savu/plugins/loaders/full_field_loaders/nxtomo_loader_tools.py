from savu.plugins.plugin_tools import PluginTools

class NxtomoLoaderTools(PluginTools):
    """A class to load tomography data from a hdf5 file
    """
    def define_parameters(self):
        """
        name:
            visibility: basic
            dtype: str
            description: A name assigned to the dataset.
            default: 'tomo'
        data_path:
            visibility: intermediate
            dtype: str
            description: Path to the data inside the file.
            default: 'entry1/tomo_entry/data/data'
        image_key_path:
            visibility: intermediate
            dtype: hdf5path
            description: Path to the image key entry inside the nxs file.
              Set this parameter to None if use this loader for radiography.
            default: 'entry1/tomo_entry/instrument/detector/image_key'
        dark:
            visibility: intermediate
            dtype: list[filepath, hdf5path, int]
            description: Specify the nexus file location where the dark field
              images are stored. Then specify the path within this nexus file,
              at which the dark images are located. The last value will be a
              scale value.
            default: '[None, None, 1]'
        flat:
            visibility: intermediate
            dtype: list[filepath, hdf5path, int]
            description: This parameter needs to be specified only if flats
              not stored in the same dataset as sample projections. Optional
              Path to the flat field data file, nxs path and scale value.
            default: '[None, None, 1]'
        angles:
            visibility: intermediate
            dtype: [float, None, list[float]]
            description: If this if 4D data stored in 3D then pass an integer
              value equivalent to the number of projections per 180 degree
              scan. If the angles parameter is set to None, then values from
              default dataset used.
            default: 'None'
        3d_to_4d:
            visibility: intermediate
            dtype: bool
            description: Many tomography datasets can be loaded. Value of
              True indicates the data must be reshaped.
            default: False
        ignore_flats:
            visibility: intermediate
            dtype: [list[int],None]
            description: List of batch numbers of flats to ignore (starting
              at 1). Useful for excluding comprimised flats in combined data
              sets containing multiple batches of interspaced flats. The
              batch indexing begins at 1.
            default: 'None'

        """
