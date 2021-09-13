from savu.plugins.plugin_tools import PluginTools

class DezingerGpuTools(PluginTools):
    """A GPU plugin to apply median-based dezinger to PROJECTION (raw) data. \
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
              description: Threshold for defecting outliers, greater is less
                sensitive. If very small, dezinger acts like a median filter.
              default: 0.1
        """
