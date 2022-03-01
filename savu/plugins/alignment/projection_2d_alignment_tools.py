from savu.plugins.plugin_tools import PluginTools


class Projection2dAlignmentTools(PluginTools):
    """A plugin to calculate horizontal-vertical shift vectors for fixing misaligned projection data
       by comparing with the re-projected data
    """

    def define_parameters(self):
        """
        upsample_factor:
              visibility: advanced
              dtype: int
              description: The upsampling factor. Registration accuracy is inversely propotional to upsample_factor.
              default: 10

        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default input dataset names.
              default: []

        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: ['shifts']
        """
