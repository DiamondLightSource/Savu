from savu.plugins.plugin_tools import PluginTools

class I13PtychoLoaderTools(PluginTools):
    """A class to load tomography data from an NXstxm file
    """
    def define_parameters(self):
        """
        mono_energy:
            visibility: basic
            dtype: float
            description: The mono energy.
            default: 9.1
        is_tomo:
            visibility: intermediate
            dtype: bool
            description: Is tomo
            default: True
        theta_step:
            visibility: intermediate
            dtype: float
            description: The theta step.
            default: 1.0
        theta_start:
            visibility: intermediate
            dtype: float
            description: The theta start.
            default: -90.0
        theta_end:
            visibility: intermediate
            dtype: float
            description: The theta end.
            default: 90.0

        """
