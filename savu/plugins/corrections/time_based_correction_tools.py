from savu.plugins.plugin_tools import PluginTools

class TimeBasedCorrectionTools(PluginTools):
    """
    Apply a time-based dark and flat field correction to data.
    """

    def define_parameters(self):
        """
        in_range:
              visibility: intermediate
              dtype: bool
              description: Set corrected values to be in the range [0, 1].
              default: False

        """