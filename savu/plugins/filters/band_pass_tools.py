from savu.plugins.plugin_tools import PluginTools

class BandPassTools(PluginTools):
    """A plugin to filter each frame with a gaussian

    """
    def define_parameters(self):
        """
        blur_width:
              visibility: basic
              dtype: list[int]
              description: Kernel size
              default: [0, 3, 3]
        type:
              visibility: basic
              dtype: str
              description: Filter type.
              options: [High, Low]
              default: High

        """
