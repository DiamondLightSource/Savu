from savu.plugins.plugin_tools import PluginTools

class TiffSaverTools(PluginTools):
    """A class to save tomography data to tiff files
    """
    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: 'VOLUME_XZ'
        prefix:
            visibility: intermediate
            dtype: [None,str]
            description: Override the default output tiff file prefix.
            default: None
        """
    def config_warn(self):
        """Do not use this plugin if the raw data is greater than 100 GB.
        """