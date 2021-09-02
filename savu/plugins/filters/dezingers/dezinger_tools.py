from savu.plugins.plugin_tools import PluginTools

class DezingerTools(PluginTools):
    """A plugin to apply median-based dezinger to PROJECTION (raw) data. \
    The plugin works in a 3D mode (kernel_size x kernel_size x kernel_size).
    """
    def define_parameters(self):
        """
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
