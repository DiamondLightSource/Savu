from savu.plugins.plugin_tools import PluginTools

class ValueMaskReplacementTools(PluginTools):
    """The function looks for a specific value in the provided second array \
(e.g. a mask) and substitutes the value in the first array with a given value.
    """
    def define_parameters(self):
        """
        seek_value:
              visibility: basic
              dtype: int
              description: The value to be located in the provided second array.
              default: 0
        new_value:
              visibility: basic
              dtype: int
              description: The value to be replaced with in the first array.
              default: 1
        """