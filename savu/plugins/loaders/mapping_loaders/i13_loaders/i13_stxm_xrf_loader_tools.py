from savu.plugins.plugin_tools import PluginTools


class I13StxmXrfLoaderTools(PluginTools):
    """A class for loading nxstxm data"""
    def define_parameters(self):
        """
        is_map:
            visibility: basic
            dtype: bool
            description: Is it a map.
            default: True

        """
