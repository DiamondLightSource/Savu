from savu.plugins.plugin_tools import PluginTools

class FresnelFilterTools(PluginTools):
    """Method similar to the Paganin filter working both on sinograms and
projections. Used to improve the contrast of the reconstruction image.

    """
    def define_parameters(self):
        """
        ratio:
              visibility: datasets
              dtype: float
              description: Control the strength of the filter. Greater is stronger
              default: 100.0
        pattern:
              visibility: basic
              dtype: str
              description: Data processing pattern
              options: [PROJECTION, SINOGRAM]
              default: SINOGRAM

        """
    def get_citation(self):
        """
        citation1:
            description: The filter built is based on the Fresnel propagator
        """