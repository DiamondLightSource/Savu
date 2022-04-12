from savu.plugins.plugin_tools import PluginTools

class RescaleIntensityTools(PluginTools):
    """The plugin performs stretching or shrinking the data intensity levels
based on skimage rescale_intensity module. Min-max scalars for rescaling can
be passed with METADATA OR by providing as an input.
    """
    def define_parameters(self):
        """
        min_value:
              visibility: basic
              dtype: [None,float]
              description: the global minimum data value.
              default: None
        max_value:
              visibility: basic
              dtype: [None,float]
              description: the global maximum data value.
              default: None
        """
