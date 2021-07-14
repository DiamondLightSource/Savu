from savu.plugins.plugin_tools import PluginTools

class ImageInterpolationTools(PluginTools):
    """A plugin to interpolate an image by a factor
    """

    def define_parameters(self):
        """
        size:
              visibility: basic
              dtype: [float, list[float]]
              description: int, float or list.
              default: 2.0
        interp:
              visibility: basic
              dtype: str
              description: The method of interpolation.
              options: [nearest, lanczos, bilinear, bicubic, cubic]
              default: 'bicubic'

        """