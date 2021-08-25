from savu.plugins.plugin_tools import PluginTools

class BaseI18MultiModalLoaderTools(PluginTools):
    """This class provides a base for all multi-modal loaders
    """
    def define_parameters(self):
        """
        fast_axis:
            visibility: basic
            dtype: str
            description: What is the fast axis called?
            default: 'x'

        scan_pattern:
            visibility: intermediate
            dtype: list
            description: What was the scan?
            default: ["rotation","x"]
        x:
            visibility: intermediate
            dtype: h5path
            description: Where is x in the file?
            default: 'entry1/raster_counterTimer01/traj1ContiniousX'
        y:
            visibility: intermediate
            dtype: [None,h5path]
            description: Where is y in the file?
            default: None
        rotation:
            visibility: intermediate
            dtype: h5path
            description: Where is rotation in the file?
            default: 'entry1/raster_counterTimer01/sc_sample_thetafine'
        monochromator:
            visibility: intermediate
            dtype: h5path
            description: Where is the monochromator?
            default: 'entry1/instrument/DCM/energy'

        """
