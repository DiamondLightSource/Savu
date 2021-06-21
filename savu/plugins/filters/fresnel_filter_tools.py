from savu.plugins.plugin_tools import PluginTools

class FresnelFilterTools(PluginTools):
    """A low-pass filter to improve the contrast of reconstructed images which
     is similar to the Paganin filter but can work on both sinograms and
     projections.
    """
    def define_parameters(self):
        """
        ratio:
              visibility: basic
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
    def citation(self):
        """
        The filter built is based on the Fresnel propagator
        """