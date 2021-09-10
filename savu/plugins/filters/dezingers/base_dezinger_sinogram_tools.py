from savu.plugins.plugin_tools import PluginTools

class BaseDezingerSinogramTools(PluginTools):
    """A base plugin to apply median-based dezinger to SINOGRAM data. \
    The plugin works in 2D or 3D mode.
    """
    def define_parameters(self):
        """
        kernel_dimension:
             visibility: intermediate
             dtype: str
             description: Select between 2D or 3D kernel for filtering
             default: 3D
        kernel_size:
             visibility: basic
             dtype: int
             description: Kernel size of the median filter.
             default: 3
        outlier_mu:
              visibility: basic
              dtype: float
              description: A threshold for detecting and removing outliers in data.\
              If set too small, dezinger acts like a median filter. The value of \
              the threshold is multiplied with a variance level in data.
              default: 0.1
        """
