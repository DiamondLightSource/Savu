from savu.plugins.plugin_tools import PluginTools

class BaseSaverTools(PluginTools):
    """A base plugin from which all data saver plugins should inherit.
    """
    def define_parameters(self):
        """
        out_datasets:
            visibility: hidden
        """