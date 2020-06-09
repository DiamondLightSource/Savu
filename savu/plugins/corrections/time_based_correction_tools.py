from savu.plugins.plugin_tools import PluginTools

class TimeBasedCorrectionTools(PluginTools):
    """Apply a time-based dark and flat field correction to data.
    """
    def define_parameters(self):
        """
        in_range:
              visibility: basic
              dtype: [range, bool]
              description: Set to True if you require values in the \
                range [0, 1].
              default: False

        """