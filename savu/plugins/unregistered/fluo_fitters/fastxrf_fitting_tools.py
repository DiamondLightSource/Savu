from savu.plugins.plugin_tools import PluginTools

class FastxrfFittingTools(PluginTools):
    """Fast fluorescence fitting with FastXRF. Needs to be on the path.
    """
    def define_parameters(self):
        """
        detector_type:
            visibility: basic
            dtype: str
            description: The type of detector
            default: 'Vortex_SDD_Xspress'

        sample_attenuators:
            visibility: intermediate
            dtype: [list, list[]]
            description: Attentuators used and thickness.
            default: []

        detector_distance:
            visibility: intermediate
            dtype: float
            description: sample to the detector in mm.
            default: 70

        exit_angle:
            visibility: intermediate
            dtype: float
            description: In degrees
            default: 90.0

        incident_angle:
           visibility: intermediate
           dtype: float
           description: In degrees
           default: 0.0

        flux:
            visibility: intermediate
            dtype: float
            description: Flux in
            default: 649055.0

        background:
           visibility: intermediate
           dtype: str
           description: Type of background subtraction.
           default: strip

        average_spectrum:
            visibility: intermediate
            dtype: [None,int]
            description: Pass an average to do the strip.
            default: None

        """
