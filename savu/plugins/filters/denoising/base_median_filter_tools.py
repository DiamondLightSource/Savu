from savu.plugins.plugin_tools import PluginTools

class BaseMedianFilterTools(PluginTools):
    """A plugin to apply 2D/3D median filter. The 3D capability is enabled
    through padding. Note that the kernel_size in 2D will be kernel_size x
    kernel_size and in 3D case kernel_size x kernel_size x kernel_size.
    """

    def define_parameters(self):
        """
        kernel_size:
             visibility: basic
             dtype: int
             description: Kernel size of the median filter.
             default: 3
        kernel_dimension:
             visibility: intermediate
             dtype: str
             description: Select between 2D or 3D kernel for filtering.
             default: 3D
        pattern:
             visibility: intermediate
             dtype: str
             options: [SINOGRAM, VOLUME_XZ]
             description: Pattern to apply this to.
             default: VOLUME_XZ

        """
