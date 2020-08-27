from savu.plugins.plugin_tools import PluginTools

class GetDataStatisticsTools(PluginTools):
    """Collect input data global statistcs.
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: list
              description: The default names
              default: ['data', 'data_statistics']
        """