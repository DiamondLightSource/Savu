from savu.plugins.plugin_tools import PluginTools

class LfovLoaderTools(PluginTools):
    """A class to load 2 scans in Nexus/hdf format into one dataset.
    """
    def define_parameters(self):
        """
        file_name:
            visibility: basic
            dtype: str
            description: The shared part of the name of each file
             (not including .nxs)
            default: 'projection'
        data_path:
            visibility: basic
            dtype: h5path
            description: Path to the data inside the file.
            default: 'entry/data/data'
        order:
            visibility: intermediate
            dtype: list[int]
            description: Order of datasets used for stitching.
            default: [1,0]
        row_offset:
            visibility: intermediate
            dtype: list[int]
            description: Offsets of row indices between datasets.
            default: [0,-1]
        stack_or_cat:
            visibility: intermediate
            dtype: str
            description: Stack or concatenate the data
             (4D and 3D respectively).
            default: 'stack'
        stack_or_cat_dim:
            visibility: intermediate
            dtype: int
            description: Dimension to stack or concatenate.
            default: 3
        axis_label:
            visibility: advanced
            dtype: str
            description: "New axis label, if required, in the form
             'name.units'."
            default: 'scan.number'
        range:
            visibility: hidden
            dtype: str
            description: No need
            default: None
        """
