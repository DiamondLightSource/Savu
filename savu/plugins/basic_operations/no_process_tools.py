from savu.plugins.plugin_tools import PluginTools

class NoProcessTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """---
        pattern:
            visibility: user
            dtype: int
            description: Explicitly state the slicing pattern.
            default: 10
        dummy:
            visibility: user
            dtype: int
            description: Dummy parameter for testing.
            default: 10

        """