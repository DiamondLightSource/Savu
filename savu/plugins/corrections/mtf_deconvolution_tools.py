from savu.plugins.plugin_tools import PluginTools

class MtfDeconvolutionTools(PluginTools):
    """Method to correct the point-spread-function effect. \
Working on raw projections and flats.
    """
    def define_parameters(self):
        """
        file_path:
              visibility: datasets
              dtype: filepath
              description: Path to file containing a 2D array of a MTF function. \
                File formats are 'npy', or 'tif'.
              default: None

        pad_width:
              visibility: intermediate
              dtype: int
              description: Pad the image before the deconvolution.
              default: 128

        """