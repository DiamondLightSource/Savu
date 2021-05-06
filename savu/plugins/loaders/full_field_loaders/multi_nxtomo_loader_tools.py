from savu.plugins.plugin_tools import PluginTools

class MultiNxtomoLoaderTools(PluginTools):
    """A class to load multiple scans in Nexus format into one dataset.
    """
    def define_parameters(self):
        """
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: 'tomo'
        file_name:
            visibility: intermediate
            dtype: [str,None]
            description: The shared part of the name of each file
              (not including .nxs).
            default: None
        data_path:
            visibility: intermediate
            dtype: h5path
            description: Path to the data inside the file.
            default: 'entry1/tomo_entry/data/data'
        dark:
            visibility: intermediate
            dtype: [list[filepath, h5path, int],list[None,None,int]]
            description: Specify the nexus file location where the dark field
              images are stored. Then specify the path within this nexus file,
              at which the dark images are located. The last value will be a
              scale value.
            default: [None, None, 1]
        flat:
            visibility: intermediate
            dtype: [list[filepath, h5path, int],list[None,None,int]]
            description: This parameter needs to be specified only if flats
              not stored in the same dataset as sample projections. Optional
              Path to the flat field data file, nxs path and scale value.
            default: [None, None, 1]
        stack_or_cat:
            visibility: intermediate
            dtype: str
            description: Stack or concatenate the data (4D and 3D respectively)
            default: 'stack'
        stack_or_cat_dim:
            visibility: intermediate
            dtype: int
            description: Dimension to stack or concatenate.
            default: 3
        axis_label:
            visibility: intermediate
            dtype: str
            description: "New axis label, if required, in the form 'name.units'"
            default: 'scan.number'
        range:
            visibility: intermediate
            dtype: list[int,int]
            description: The start and end of file numbers
            default: [0,10]
        angles:
            visibility: intermediate
            dtype: [str, int, None]
            description: If this is 4D data stored in 3D then pass an integer
              value equivalent to the number of projections per 180 degree
              scan. If the angles parameter is set to None, then values from
              default dataset used.
            default: None

        """
