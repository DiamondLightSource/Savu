from savu.plugins.plugin_tools import PluginTools

class InpaintingTools(PluginTools):
    """A plugin to apply 2D/3D inpainting technique to data. If there
is a chunk of data missing or one needs to inpaint some data features.
    """
    def define_parameters(self):
        """
        mask_range:
              visibility: basic
              dtype: list[float,float]
              description: generate mask as a threshold of the input image given the intensity range (ignored if the mask is provided).
              default: [1.0,100]
        method:
              visibility: intermediate
              dtype: str
              options: [INPAINT_EUCL_WEIGHTED, NONLOCAL_MARCH, DIFFUSION]
              description: Choose inpainting method
              default: INPAINT_EUCL_WEIGHTED
        iterations:
              visibility: basic
              dtype: int
              description: the number of iterations to perform the inpainting (controls the smoothing level)
              default: 5
        windowsize_half:
              visibility: intermediate
              dtype: int
              description: half-size of the smoothing window, increase size for more smoothing
              default: 7
              dependency:
                method: [INPAINT_EUCL_WEIGHTED]
        search_window_increment:
              visibility: advanced
              dtype: int
              description: the increment value with which the searching window is growing in iterations
              default: 1
              dependency:
                method: [NONLOCAL_MARCH]
        regularisation_parameter:
              visibility: basic
              dtype: float
              description: regularisation parameter for diffusion
              default: 1000
              dependency:
                method: [DIFFUSION]
        time_marching_parameter:
              visibility: intermediate
              dtype: float
              description: ensuring convergence of the diffusion scheme
              default: 0.00001
              dependency:
                method: [DIFFUSION]
        """
