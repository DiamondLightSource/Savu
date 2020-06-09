from savu.plugins.plugin_tools import PluginTools

class DezingerSinogramTools(PluginTools):
    """Method to remove scratches in the reconstructed image caused by zingers
    """
    def define_parameters(self):
        """
        tolerance:
              visibility: basic
              dtype: float
              description: Threshold for detecting zingers, greater is less \
                sensitive.
              default: 0.08

        """