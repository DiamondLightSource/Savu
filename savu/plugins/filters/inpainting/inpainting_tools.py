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
              description: mask for inpainting is set as a threshold in a range.
              default: [1.0,100]
        iterations:
              visibility: basic
              dtype: float
              description: controls the smoothing level of the inpainted region.
              default: 50
        windowsize_half:
              visibility: basic
              dtype: int
              description: half-size of the smoothing window.
              default: 3
        sigma:
              visibility: basic
              dtype: float
              description: maximum value for the inpainted region.
              default: 0.5
        pattern:
              visibility: basic
              dtype: str
              description: Pattern to apply these to.
              default: SINOGRAM

        """