from savu.plugins.plugin_tools import PluginTools

class StatsTools(PluginTools):
    """
    Grabs a selection of statistics.
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: the output dataset.
              default: ['stats']
        required_stats:
              visibility: basic
              dtype: list
              description: Create a list of required stats calcs.
              default: ['max']
        direction:
              visibility: basic
              dtype: str
              description: Which direction to perform this.
              default: PROJECTION
        """