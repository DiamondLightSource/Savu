from savu.plugins.plugin_tools import PluginTools

class GeoDistanceTools(PluginTools):
    """Geodesic transformation of images with mask initialisation.
    """
    def define_parameters(self):
        """
        lambda:
            visibility: intermediate
            dtype: float
            description: Weighting between 0 and 1
            default: 0.5

        iterations:
            visibility: basic
            dtype: int
            description: The number of iterations for raster scanning.
            default: 4

        out_datasets:
            visibility: intermediate
            dtype: [list[],list[str]]
            description: The default names.
            default: "['GeoDist, 'max_values']"

        """
