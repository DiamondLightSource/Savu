from savu.plugins.plugin_tools import PluginTools

class MaskEvolve3dTools(PluginTools):
    """Fast segmentation by evolving the given 3D mask, the initial mask must be given
precisely through the object, otherwise segmentation will be incorrect.

    """
    def define_parameters(self):
        """
        threshold:
            visibility: basic
            dtype: float
            description: Important parameter to control mask propagation.
            default: 1.0

        method:
            visibility: basic
            dtype: str
            description: 'Method to collect statistics from the mask (mean, median, value).'
            default: mean

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations.
            default: 500

        connectivity:
            visibility: intermediate
            dtype: int
            description: The connectivity of the local neighbourhood.
            default: 6

        out_datasets:
            visibility: intermediate
            dtype: list
            description: The default names.
            default: '[MASK_EVOLVED]'

        """
