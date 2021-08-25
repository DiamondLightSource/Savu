from savu.plugins.plugin_tools import PluginTools

class NoProcessPluginTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """
        pattern:
              visibility: intermediate
              dtype: [None,str]
              description: Explicitly state the slicing pattern.
              default: None
        dummy:
              visibility: basic
              dtype: int
              description: Dummy parameter for testing.
              default: 10
        """
