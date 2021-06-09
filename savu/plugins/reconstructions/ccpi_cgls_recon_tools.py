from savu.plugins.plugin_tools import PluginTools

class CcpiCglsReconTools(PluginTools):
    """A Plugin to run the CCPi implementation of the CGLS reconstruction
algorithm.
    """

    def define_parameters(self):
        """

        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations to perform.
            default: 5

        resolution:
            visibility: intermediate
            dtype: float
            description: Number of output voxels (res = n_pixels/n_voxels),
              set res > 1 for reduced resolution.
            default: 1

        n_frames:
            visibility: intermediate
            dtype: int
            description:  This algorithm requires a multiple of 8 frames at a
                time for processing and this number may affect performance 
                depending on your data size.
            options: [8,16,24,32]
            default: 16

        init_vol:
            visibility: hidden
            dtype: [None,str]
            description: Not an option.
            default: None

        """
