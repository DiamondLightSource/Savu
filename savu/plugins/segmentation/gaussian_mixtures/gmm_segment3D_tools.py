from savu.plugins.plugin_tools import PluginTools

class GmmSegment3dTools(PluginTools):
    """A Plugin to segment data using Gaussian Mixtures from scikit
    """
    def define_parameters(self):
        """
        classes:
            visibility: basic
            dtype: int
            description: The number of classes for GMM
            default: 4
        """
