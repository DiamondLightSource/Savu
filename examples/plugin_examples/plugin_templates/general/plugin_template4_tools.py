from savu.plugins.plugin_tools import PluginTools

class PluginTemplate4Tools(PluginTools):
    """
    A template for a plugin that takes in two datasets and returns one dataset,
    e.g. absorption correction.
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None
        in_datasets:
            visibility: datasets
            dtype: [list[str],list[]]
            description: Override the in_datasets parameter
            default: ['fluo', 'stxm']
        preview:
            visibility: basic
            dtype: preview
            description: Reduce the number of sinograms of stxm to match fluo
            default: []
        out_datasets:
            visibility: datasets
            dtype: [list[str],list[]]
            description: Override the out_datasets parameter
            default: ['fluo']

        """