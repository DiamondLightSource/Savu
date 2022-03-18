from savu.plugins.plugin_tools import PluginTools

class MinAndMaxTools(PluginTools):
    """A plugin to calculate the min and max values of each slice (as determined
by the pattern parameter)
    """
    def define_parameters(self):
        """
        method:
           visibility: basic
           dtype: str
           options: ['extrema', 'percentile']
           description: Method to find the global min and the global max.
           default: percentile

        p_range:
            visibility: basic
            dtype: list[float,float]
            description: Percentage range if use the 'percentile' method.
            default: [0.0, 100.0]

        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data.
            default: VOLUME_XZ

        smoothing:
            visibility: intermediate
            dtype: bool
            description: Apply a smoothing filter or not.
            default: True

        masking:
            visibility: intermediate
            dtype: bool
            description: Apply a circular mask or not.
            default: True

        ratio:
            visibility: intermediate
            dtype: [None,float]
            description: Used to calculate the circular mask. If not provided,
              it is calculated using the center of rotation.
            default: None

        out_datasets:
             visibility: datasets
             dtype: [list[],list[str]]
             description: The default names.
             default: ['the_min','the_max']
        """
