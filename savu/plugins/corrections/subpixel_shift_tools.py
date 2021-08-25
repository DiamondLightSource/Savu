from savu.plugins.plugin_tools import PluginTools

class SubpixelShiftTools(PluginTools):
    """
    A plugin to apply a sub-pixel correction to images.
    """

    def define_parameters(self):
        """
        x_shift:
            visibility: basic
            dtype: float
            description: The shift in x for the output image in pixels. 
                Positive values correspond to data being shifted towards larger
                indices.
            default: 0.0

        transform_module:
            visibility: intermediate
            dtype: str
            description: The module to be used for image translation.  Choose
                a method in the Skimage package or in the Scipy package.
            default: scipy
            options: [scipy, skimage]

        """