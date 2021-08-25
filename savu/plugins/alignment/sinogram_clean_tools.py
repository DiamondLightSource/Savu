from savu.plugins.plugin_tools import PluginTools

class SinogramCleanTools(PluginTools):
    """
    Clean the sinogram by applying a mask in Fourier space.
    """

    def define_parameters(self):
        """
        ratio:
              visibility: basic
              dtype: float
              description:  The ratio between the size of object and FOV of
                the camera.
              default: 2.0
        row_drop:
              visibility: intermediate
              dtype: int
              description: 'Drop lines around vertical center of the mask
                scipy.optimize.curve_fit.'
              default: 20
        """
