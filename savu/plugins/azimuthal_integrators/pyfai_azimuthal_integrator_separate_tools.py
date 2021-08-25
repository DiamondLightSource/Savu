from savu.plugins.plugin_tools import PluginTools

class PyfaiAzimuthalIntegratorSeparateTools(PluginTools):
    """1D azimuthal integrator by pyFAI
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Names assigned to datasets created as output to the
                  plugin.
              default: ['powder','spots']
        percentile:
              visibility: intermediate
              dtype: int
              description: Percentile to threshold
              default: 50
        num_bins_azim:
              visibility: basic
              dtype: int
              description: Number of azimuthal bins.
              default: 20

        """
