from savu.plugins.plugin_tools import PluginTools

class BasePtychoTools(PluginTools):
    """A base plugin for doing ptychography. Other ptychography plugins should
    inherit from this.
    """
    def define_parameters(self):
        """
        out_datasets:
              default: "['probe', 'object_transmission', 'positions']"
        """