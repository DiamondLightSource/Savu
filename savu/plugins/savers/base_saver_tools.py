from savu.plugins.plugin_tools import PluginTools

class BaseSaverTools(PluginTools):
    """A base plugin from which all data saver plugins should inherit.
    """
    def define_parameters(self):
        """
        out_datasets:
            visibility: hidden
            dtype: list
            description: none
            default: []
        in_datasets:
            visibility: advanced
            dtype: list
            description: none
            default: []
        """