from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class Hdf5SaverTools(PluginTools):
    """A class to save tomography data to a hdf5 file
    """
    def define_parameters(self):
        """---
        pattern:
            visibility: basic
            dtype: str
            description: Optimise data storage to this access pattern
              'optimum' will automate this process by choosing the output
              pattern from the previous plugin, if it exists, else the
              first pattern.
            default: 'optimum'
        """