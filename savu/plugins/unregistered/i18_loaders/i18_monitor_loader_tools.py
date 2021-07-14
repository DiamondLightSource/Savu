from savu.plugins.plugin_tools import PluginTools

class I18MonitorLoaderTools(PluginTools):
    """A class to load I18's data from a monitor file
    """
    def define_parameters(self):
        """
        monitor_detector:
            visibility: basic
            dtype: str
            description: Path to monitor.
            default: 'entry1/raster_counterTimer01/I0'
        name:
            visibility: basic
            dtype: str
            description: The new name assigned to the dataset.
            default: 'monitor'

        """
