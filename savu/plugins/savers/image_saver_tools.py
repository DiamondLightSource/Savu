from savu.plugins.plugin_tools import PluginTools

class ImageSaverTools(PluginTools):
    """A class to save tomography data to image files.  Run the MaxAndMin plugin
before this to rescale the data.
    """
    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data.
            default: VOLUME_XZ

        format:
            visibility: basic
            dtype: str
            description: Image format.
            default: tif

        num_bit:
            visibility: basic
            dtype: int
            description: Bit depth of the tiff format (8, 16 or 32).
            default: 16
            options: [8,16,32]

        max:
            visibility: intermediate
            dtype: [None,float]
            description: Global max for tiff scaling.
            default: None

        min:
           visibility: intermediate
           dtype: [None,float]
           description: Global min for tiff scaling.
           default: None

        jpeg_quality:
            visibility: intermediate
            dtype: int
            description: JPEG encoding quality (1 is worst, 100 is best).
            default: 75

        prefix:
             visibility: intermediate
             dtype: [None,str]
             description: Override the default output jpg file prefix
             default: None
        """

    def config_warn(self):
        """Do not use this plugin if the raw data is greater than 100 GB.
        """