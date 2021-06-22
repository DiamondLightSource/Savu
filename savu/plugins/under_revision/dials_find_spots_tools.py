from savu.plugins.plugin_tools import PluginTools

class DialsFindSpotsTools(PluginTools):
    """Finding the single crystal peaks with dials
    """
    def define_parameters(self):
        """
        spotsize:
              visibility: basic
              dtype: int
              description: approximate maximum spot size.
              default: 45

        """