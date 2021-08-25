from savu.plugins.plugin_tools import PluginTools

class DarkFlatFieldCorrectionTools(PluginTools):
    """A Plugin to apply a simple dark and flat field correction to data.
    """
    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            options: [SINOGRAM, PROJECTION]
            description: Data processing pattern
            default: PROJECTION
        lower_bound:
            visibility: intermediate
            dtype: [None,float]
            description: Set all values below the lower_bound to this value.
            default: None
        upper_bound:
            visibility: intermediate
            dtype: [None,float]
            description: Set all values above the upper bound to this value.
            default: None
        warn_proportion:
            visibility: intermediate
            dtype: float
            description: Output a warning if this proportion of values, or 
                  greater, are below and/or above the lower/upper bounds. 
                  E.g. Enter 0.05 for 5%.
            default: 0.05

        """