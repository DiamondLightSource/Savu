from savu.plugins.plugin_tools import PluginTools

class OtsuThreshTools(PluginTools):
    """A Plugin to segment the data using Otsu's method
    """

    def define_parameters(self):
        """
        cropping:
            visibility: basic
            dtype: bool
            options: [True, False]
            description: Calculate cropping values based on Otsu segmentation (will not actually crop the output)
            default: False

        directions:
            visibility: intermediate
            dtype: list[str]
            description: Which directions to crop out, relative to sample.
            default: ["left", "above", "right", "below"]

        buffer:
            visibility: intermediate
            dtype: int
            description: Expand cropping values by this amount to give some space around cropped object.
            default: 20


        pattern:
             visibility: intermediate
             dtype: str
             options: [PROJECTION, SINOGRAM, VOLUME_XZ]
             description: Pattern to apply this to.
             default: PROJECTION

        """
        pass
