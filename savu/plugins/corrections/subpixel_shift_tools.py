from savu.plugins.plugin_tools import PluginTools

class SubpixelShiftTools(PluginTools):
    """A plugin to apply a sub-pixel correction to images, for example to allow
    subpixel alignment for the AstraGpu plugin.
    """
    def define_parameters(self):
        """
        x_shift:
            visibility: intermediate
            dtype: float
            description: "The shift in x for the output image in pixels. Positive
            values correspond to data being shifted towards larger indices."
            default: 0.0

        transform_module:
            visibility: intermediate
            dtype: str
            description: "The module (skimage|scipy) to be used for image
            translation. skimage corresponds to skimage.transform.SimilarityTransform
            while scipy corresponds to scipy.ndimage.interpolation."
            default: skimage
            options: [skimage, scipy]


        """