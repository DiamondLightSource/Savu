from savu.plugins.plugin_tools import PluginTools

class StatsTools(PluginTools):
    """
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: list
              description: the output dataset.
              default: ['stats']
        required_stats:
              visibility: intermediate
              dtype: list
              description: Create a list of required stats calcs.
              default: ['max']
        direction:
              visibility: intermediate
              dtype: str
              description: Which direction to perform this.
              default: PROJECTION
        """