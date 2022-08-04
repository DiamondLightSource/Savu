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

        interpolation_order:
              visibility: advanced
              dtype: int
              description: The interpolation order, 0-Nearest-neighbor, 1-bilinear, 2-biquadratic, 3-bicubic, 4-biquartic(splines), 5-biquintic(splines).
              default: 5
              dependency:
                  registration:
                   True

        registration:
              visibility: basic
              dtype: bool
              description: Set as True to transform the projections with the shifts that are calculated, or set as False to calculate the shifts but not apply them
              default: False

        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Two datasets to register to each other, given as [static_reference, dataset_to_register_to_reference]. The order of datasets in the list is important to avoid divergence in the iterative alignment method.
              default: []

        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names. If registration is set to true, remove the second dataset.
              default: [shifts, shifted_projections]              
        """
