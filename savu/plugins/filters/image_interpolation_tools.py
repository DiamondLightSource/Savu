from savu.plugins.plugin_tools import PluginTools

class ImageInterpolationTools(PluginTools):
    """A plugin to interpolate an image by a factor
    """
    def define_parameters(self):
        """
        size:
              visibility: basic
              dtype: [float, tuple]
              description: int, float or tuple.
              default: 2.0
        interp:
              visibility: basic
              dtype: str
              description: nearest lanczos bilinear bicubic cubic.
              options: [nearest, lanczos, bilinear, bicubic, cubic]
              default: 'bicubic'

        """