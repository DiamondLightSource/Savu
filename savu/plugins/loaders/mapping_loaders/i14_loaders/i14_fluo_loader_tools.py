from savu.plugins.plugin_tools import PluginTools

class I14FluoLoaderTools(PluginTools):
    """A class to load i14s xrf data
    """
    def define_parameters(self):
        """
        mono_path:
            visibility: basic
            dtype: h5path
            description: The mono energy.
            default: '/entry/instrument/beamline/DCM/dcm_energy'

        """
