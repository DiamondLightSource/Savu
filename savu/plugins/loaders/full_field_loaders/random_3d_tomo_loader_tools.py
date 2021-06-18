from savu.plugins.plugin_tools import PluginTools

class Random3dTomoLoaderTools(PluginTools):
    """A hdf5 dataset of a specified size is created at runtime using numpy
    random sampling (numpy.random), saved with relevant meta_data to a NeXus
    file, and used as input. It recreates the behaviour of the nxtomo loader
    but with random data.  The input file path passed to Savu will be ignored
    (use a dummy).
    Note: Further extensions planned to allow the generated data to be
    re-loaded with the nxtomo_loader.
    """
    def define_parameters(self):
        """
        axis_labels:
            visibility: basic
            dtype: list[str]
            description: A list of axis labels.
            default: "['rotation_angle.degrees', 'detector_y.angles', 'detector_x.angles']"
        patterns:
            visibility: hidden
            dtype: list[str]
            description: Patterns.
            default: "['SINOGRAM.0c.1s.2c', 'PROJECTION.0s.1c.2c']"
        dataset_name:
            visibility: hidden
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        image_key:
            visibility: intermediate
            dtype: list
            description: 'Specify position of darks and flats (in that order)
              in the data.'
            default: [[0, 1], [2, 3]]

        """
