from savu.plugins.plugin_tools import PluginTools


class TomoPhantomLoaderTools(PluginTools):
    """A hdf5 dataset of a specified size is created at runtime using Tomophantom
    to generate synthetic data , saved with relevant meta_data to a NeXus
    file, and used as input. It recreates the behaviour of the nxtomo loader
    but with synthetic data.  The input file path passed to Savu will be ignored
    (use a dummy).
    """

    def define_parameters(self):
        """
        axis_labels:
            visibility: basic
            dtype: list[str]
            description: A list of axis labels.
            default: "['rotation_angle.degrees', 'detector_y.pixels', 'detector_x.pixels']"
        axis_labels_phantom:
            visibility: hidden
            dtype: list[str]
            description: A list of axis labels.
            default: "['detector_z.pixels', 'detector_y.pixels', 'detector_x.pixels']"
        patterns:
            visibility: hidden
            dtype: list[str]
            description: projection data object patterns.
            default: "['SINOGRAM.0c.1s.2c', 'PROJECTION.0s.1c.2c']"
        patterns_tomo2:
            visibility: hidden
            dtype: list[str]
            description: Phantom data object patterns.
            default: "['VOLUME_XZ.0c.1s.2c', 'VOLUME_XY.0s.1c.2c']"
        out_datasets:
            visibility: basic
            dtype: list[str]
            description: The names assigned to the datasets.
            default: "['synth_proj_data', 'phantom']"
        """
