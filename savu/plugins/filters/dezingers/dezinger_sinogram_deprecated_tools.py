from savu.plugins.plugin_tools import PluginTools

class DezingerSinogramDeprecatedTools(PluginTools):
    """Method to remove scratches in the reconstructed image caused by
zingers. Remove zingers (caused by scattered X-rays hitting the CCD chip
directly) Threshold for detecting zingers, greater is less sensitive.
    """
    def define_parameters(self):
        """
        tolerance:
              visibility: basic
              dtype: float
              description: Threshold for detecting zingers, greater is less
                sensitive.
              default: 0.08

        """