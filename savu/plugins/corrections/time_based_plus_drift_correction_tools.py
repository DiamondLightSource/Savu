from savu.plugins.plugin_tools import PluginTools

class TimeBasedPlusDriftCorrectionTools(PluginTools):
    """
    Apply a time-based dark and flat field correction on data with an image
    drift using linear interpolation and template matching.
    """
    
    def define_parameters():
        """
        template:
            visibility: basic
            description: Region on the detector used to track the drift
            dtype: list[str]
            default: [100:200, 100:200]
        """
