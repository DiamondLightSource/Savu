from savu.plugins.plugin_tools import PluginTools

class I18FluoLoaderTools(PluginTools):
    """A class to load I18's data from an NXstxm file
    """
    def define_parameters(self):
        """
        fluo_detector:
            visibility: basic
            dtype: str
            description: Path to fluo.
            default: 'entry1/xspress3/AllElementSum'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'fluo'

        """
