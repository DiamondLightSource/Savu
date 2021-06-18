from savu.plugins.plugin_tools import PluginTools

class ProjectionVerticalAlignmentTools(PluginTools):
    """Correct for vertical shift over projection images.
    """

    def config_warn(self):
        """Requires the PluginShift plugin to precede it.
        """
