from savu.plugins.plugin_tools import PluginTools

class ValueSubstitutionTools(PluginTools):
    """The function looks for a specific value in the provided second dataset
(e.g. a mask image) and substitutes it with a given value.
    """
    def define_parameters(self):
        """
        seek_value:
              visibility: basic
              dtype: float
              description: The value to be located in the second dataset.
              default: 0.0
        new_value:
              visibility: basic
              dtype: float
              description: The value to be replaced with in the first dataset.
              default: 1.0
        pattern:
            visibility: advanced
            dtype: str
            options: [SINOGRAM, PROJECTION, VOLUME_XZ, VOLUME_YZ]
            description: Pattern to apply this to.
            default: 'VOLUME_XZ'
        """
