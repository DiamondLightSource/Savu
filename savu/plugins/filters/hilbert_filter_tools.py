from savu.plugins.plugin_tools import PluginTools

class HilbertFilterTools(PluginTools):
    """A plugin to apply Hilbert filter horizontally for tomographic
   reconstruction of phase gradient images. Note to use it before Vocentering,
   set "log" to "False" and "FBP_filter" to "None" in a reconstruction plugin.
   No parameter is required.
    """
