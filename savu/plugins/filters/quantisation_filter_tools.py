from savu.plugins.plugin_tools import PluginTools

class QuantisationFilterTools(PluginTools):
    """A plugin to quantise an image into discrete levels.
    """
    def define_parameters(self):
        """
        explicit_min_max:
              visibility: intermediate
              dtype: bool
              description: "False if min/max intensity comes from the
                metadata, True if it's user-defined. "
              default: False
        min_intensity:
              visibility: intermediate
              dtype: int
              description: Global minimum intensity.
              default: 0
        max_intensity:
              visibility: intermediate
              dtype: int
              description: Global maximum intensity.
              default: 65535
        levels:
              visibility: intermediate
              dtype: int
              description: Number of levels.
              default: 5

        """
