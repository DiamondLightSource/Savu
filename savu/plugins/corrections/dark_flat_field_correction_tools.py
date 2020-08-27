from savu.plugins.plugin_tools import PluginTools

class DarkFlatFieldCorrectionTools(PluginTools):
    """A Plugin to apply a simple dark and flat field correction to data.
    """
    def define_parameters(self):
        """
        pattern:
            visibility: advanced
            dtype: str
            options: [SINOGRAM, PROJECTION]
            description: Data processing pattern
            default: PROJECTION
        lower_bound:
            visibility: advanced
            dtype: float
            description: Set all values below the lower_bound to this value.
            default: None
        upper_bound:
            visibility: advanced
            dtype: float
            description: Set all values above the upper bound to this value.
            default: None
        warn_proportion:
            visibility: advanced
            dtype: float
            description:
              summary: Output a warning if this proportion of values, or greater, are below and/or above the lower/upper bounds
              verbose: 'Enter 0.05 for 5%'
            default: 0.05

        """