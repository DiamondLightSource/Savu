from savu.plugins.plugin_tools import PluginTools

class I08FluoLoaderTools(PluginTools):
    """A class to load i08s xrf data
    """
    def define_parameters(self):
        """
        mono_path:
            visibility: basic
            dtype: h5path
            description: The mono energy.
            default: '/entry/instrument/PlaneGratingMonochromator/pgm_energy'

        """
