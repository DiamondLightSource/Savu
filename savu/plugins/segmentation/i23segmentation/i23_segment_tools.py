from savu.plugins.plugin_tools import PluginTools

class I23SegmentTools(PluginTools):
    """A Plugin to segment reconstructed data from i23 beamline. The projection data
should be first reconstructed iteratively using the ToMoBAR plugin. The goal of
the segmentation plugin is to cluster and segment data using Gaussian Mixtures
and then apply iterative model-based segmentation to further process the obtained
mask. https://github.com/dkazanc/i23seg
    """
    def define_parameters(self):
        """
        correction_window:
            visibility: basic
            dtype: int
            description: The size of the correction window
            default: 9

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations for segmentation.
            default: 10

        out_datasets:
            visibility: intermediate
            dtype: list
            description: Default out dataset names.
            default: "['maskGMM4', 'maskGMM4_proc', 'maskGMM5', 'maskGMM5_proc']"

        """
