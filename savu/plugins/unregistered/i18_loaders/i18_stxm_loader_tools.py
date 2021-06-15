from savu.plugins.plugin_tools import PluginTools

class I18StxmLoaderTools(PluginTools):
    """A class to load I18's data from a Nxstxm file
    """
    def define_parameters(self):
        """
        stxm_detector:
            visibility: basic
            dtype: str
            description: Path to stxm.
            default: 'entry1/raster_counterTimer01/It'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'stxm'

        """
