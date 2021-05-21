from savu.plugins.plugin_tools import PluginTools

class BandPassTools(PluginTools):
    """A plugin to filter each frame with a BandPass T

    """
    def define_parameters(self):
        """
        blur_width:
              visibility: basic
              dtype: tuple
              description: Kernel size
              default: (0, 3, 3)
        type:
              visibility: basic
              dtype: str
              description: 'Filter type (High|Low).'
              options: [High, Low]
              default: High

        """