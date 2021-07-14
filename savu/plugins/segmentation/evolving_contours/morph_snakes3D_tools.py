from savu.plugins.plugin_tools import PluginTools

class MorphSnakes3dTools(PluginTools):
    """A Plugin to 3D segment reconstructed data using
Morphsnakes module. When initialised with a mask, the active contour
propagates to find the minimum of energy (a possible edge countour).
    """

    def define_parameters(self):
        """
        lambda1:
            visibility: basic
            dtype: int
            description: 'Weight parameter for the outer region, if lambda1
              is larger than lambda2, the outer region will contain a larger
              range of values than the inner region.'
            default: 1

        lambda2:
            visibility: basic
            dtype: int
            description: 'Weight parameter for the inner region, if lambda2
              is larger than lambda1, the inner region will contain a larger
              range of values than the outer region.'
            default: 1

        smoothing:
            visibility: intermediate
            dtype: int
            description: 'Number of times the smoothing operator is applied
              per iteration, reasonable values are around 1-4 and larger
              values lead to smoother segmentations.'
            default: 1

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations.
            default: 350


        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: The default names
            default: ['MASK_MORPH_EVOLVED3D']

        """
