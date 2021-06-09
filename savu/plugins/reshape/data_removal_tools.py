from savu.plugins.plugin_tools import PluginTools

class DataRemovalTools(PluginTools):
    """A class to remove any unwanted data from the specified pattern frame.
    """
    def define_parameters(self):
        """
        indices:
            visibility: basic
            dtype: [list, str, None]
            description: A list or range of values to remove, e.g. [0, 1, 2]
              , 0:2 (start:stop) or 0:2:1 (start:stop:step).
            default: None
        pattern:
            visibility: basic
            dtype: str
            description: Explicitly state the slicing pattern.
            default: 'SINOGRAM'
        dim:
            visibility: basic
            dtype: int
            description: Data dimension to reduce.
            default: 0

        """

