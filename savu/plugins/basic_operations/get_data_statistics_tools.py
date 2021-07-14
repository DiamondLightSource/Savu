from savu.plugins.plugin_tools import PluginTools

class GetDataStatisticsTools(PluginTools):
    """Collects data global statistcs (max, min, sum, mean) and put it in metadata.
    """
    def define_parameters(self):
        """
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: The default names
              default: ['data', 'data_statistics']
        pattern:
            visibility: intermediate
            dtype: str
            options: [SINOGRAM, PROJECTION, VOLUME_XZ, VOLUME_YZ]
            description: Pattern to apply this to.
            default: 'VOLUME_XZ'
        """
