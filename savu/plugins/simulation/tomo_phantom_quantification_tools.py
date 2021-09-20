from savu.plugins.plugin_tools import PluginTools


class TomoPhantomQuantificationTools(PluginTools):
    """A plugin to calculate some standard image quality metrics
    """

    def define_parameters(self):
        """
        pattern:
             visibility: intermediate
             dtype: str
             options: [SINOGRAM, PROJECTION, VOLUME_XZ]
             description: Pattern to apply this to.
             default: SINOGRAM
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: "['quantification_values']"

        """
