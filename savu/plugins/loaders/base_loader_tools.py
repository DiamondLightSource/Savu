from savu.plugins.plugin_tools import PluginTools

class BaseLoaderTools(PluginTools):
    """
    A base class for loader plugins. A base plugin from which all data loader
    plugins should inherit.
    """

    def define_parameters(self):
        """
        preview:
              visibility: basic
              dtype: preview
              description: A slice list of required frames.
              default: []
        in_datasets:
              # inherited but not needed
              visibility: ignore
        out_datasets:
              # inherited but not needed
              visibility: ignore

        """
