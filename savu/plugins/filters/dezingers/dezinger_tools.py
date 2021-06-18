from savu.plugins.plugin_tools import PluginTools

class DezingerTools(PluginTools):
    """A plugin to apply 2D/3D median-based dezinger. The 3D capability is enabled\
    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size
    and in 3D case kernel_size x kernel_size x kernel_size.
    """
    def define_parameters(self):
        """
        outlier_mu:
              visibility: basic
              dtype: float
              description: Threshold for defecting outliers, greater is less
                sensitive. If very small, dezinger acts like a median filter.
              default: 1.0
        kernel_size:
              visibility: basic
              dtype: int
              description: Kernel size of the median filter.
              default: 3
        dimension:
              visibility: intermediate
              dtype: str
              description: dimensionality of the filter 2D/3D.
              default: 3D
        pattern:
              visibility: basic
              dtype: str
              description: Pattern to apply this to.
              default: PROJECTION

        """

    def config_warn(self):
        """The dezinger plugin should be applied to normalised data
        (e.g. AFTER DarkFlatFieldCorrection)
        """
