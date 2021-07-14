from savu.plugins.plugin_tools import PluginTools

class PluginTemplate5Tools(PluginTools):
    """
    A plugin template with one in_dataset and two out_datasets that do not
    resemble the in_dataset and are not retained by the framework,
    e.g. vo_centering.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None
        preview:
            visibility: basic
            dtype: preview
            description: Reduce the size of the data temporarily for this plugin
            default: []
        """