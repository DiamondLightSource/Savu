from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class BaseCorrectionTools(PluginTools):
    """A base class for dark and flat field correction plugins.
    """
    def define_parameters(self):
        """---
        in_datasets:
            visibility: hidden
            dtype: '[int]'
            description:
            default: []
        out_datasets:
            visibility: hidden
            dtype: '[int]'
            description:
            default: []

        """