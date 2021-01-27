from savu.plugins.plugin_tools import PluginTools

class MedianFilterGpuTools(PluginTools):
    """A plugin to apply 2D/3D median filter on a GPU. The 3D capability is enabled\
    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size
    and in 3D case kernel_size x kernel_size x kernel_size.
    """

    def define_parameters(self):
        """
        kernel_size:
             visibility: basic
             dtype: int
             description: Kernel size of the median filter.
             default: 3
        dimension:
             visibility: advanced
             dtype: str
             description: Dimensionality of the filter 2D/3D.
             default: 3D
        pattern:
             visibility: advanced
             dtype: str
             description: Pattern to apply this to.
             default: PROJECTION

        """