from savu.plugins.plugin_tools import PluginTools

class DataRemovalTools(PluginTools):
    """A class to remove any unwanted data from the specified pattern frame.
    """
    def define_parameters(self):
        """
        indices:
            visibility: intermediate
            dtype: list
            description: A list or range of values to remove, e.g. [0, 1, 2]\
              , 0:2 (start:stop) or 0:2:1 (start:stop:step).
            default: None
        pattern:
            visibility: intermediate
            dtype: int
            description: Explicitly state the slicing pattern.
            default: 'SINOGRAM'
        dim:
            visibility: intermediate
            dtype: int
            description: Data dimension to reduce.
            default: 0

        """

