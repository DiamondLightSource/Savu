from savu.plugins.plugin_tools import PluginTools

class PymcaTools(PluginTools):
    """Uses pymca to fit spectral data
    """
    def define_parameters(self):
        """
        config:
              visibility: intermediate
              dtype: filepath
              description: Path to the config file
              default: Savu/test_data/data/test_config.cfg

        """
