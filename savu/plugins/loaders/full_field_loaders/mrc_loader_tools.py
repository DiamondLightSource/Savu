from savu.plugins.plugin_tools import PluginTools

class MrcLoaderTools(PluginTools):
    """Load Medical Research Council (MRC) formatted image data.
    """
    def define_parameters(self):
        """
        angles:
            visibility: basic
            dtype: [str, int, None]
            description: A python statement to be evaluated
              (e.g np.linspace(0, 180, nAngles)) or a txt file.
            default: None
        name:
            visibility: intermediate
            dtype: str
            description: The name assigned to the dataset
            default: tomo
        """
