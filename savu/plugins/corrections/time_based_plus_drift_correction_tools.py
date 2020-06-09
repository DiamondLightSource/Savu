from savu.plugins.plugin_tools import PluginTools

class TimeBasedPlusDriftCorrectionTools(PluginTools):
    """Apply a time-based dark and flat field correction on data with an \
image drift using linear interpolation and template matching.
    """