from savu.plugins.plugin_tools import PluginTools

class PluginTemplate2Tools(PluginTools):
    """
    A simple plugin template with multiple input and output datasets.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None
        out_datasets:
            visibility: datasets
            dtype: [list[str],list[]]
            description: Overriding the out_datasets parameter
            default: ['in_datasets[1]', 'data2']
        """