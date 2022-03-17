from savu.plugins.plugin_tools import PluginTools


class Projection2dAlignmentTools(PluginTools):
    """A plugin to perform alignment (registration) if two images, e.g. two projections. The result is horizontal-vertical shift vectors written into the experimental metadata.
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
              description: Two datasets to register to each other, given as [static_reference, dataset_to_register_to_reference]. The order of datasets in the list is important to avoid divergence in the iterative alignment method.
              default: []

        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: ['shifts']
        """
