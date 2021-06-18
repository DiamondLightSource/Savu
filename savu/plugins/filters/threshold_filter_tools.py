from savu.plugins.plugin_tools import PluginTools

class ThresholdFilterTools(PluginTools):
    """A plugin to quantise an image into discrete levels.

    """
    def define_parameters(self):
        """
        explicit_threshold:
              visibility: basic
              dtype: bool
              description: False if plugin calculates black/white threshold,
                True if it's user-defined.
              default: True
        intensity_threshold:
              visibility: basic
              dtype: int
              description: Threshold for black/white quantisation.
              default: 32768

        """