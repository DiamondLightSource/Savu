from savu.plugins.plugin_tools import PluginTools

class BaseTools(PluginTools):
    """The base class from which all plugins should inherit.
    """
    def define_parameters(self):
        """
        in_datasets:
            visibility: datasets
            dtype: [list[str], list[]]
            description: 
                summary: A list of the dataset(s) to process.
                verbose: >
                    A list of strings, where each string gives the name of a
                    dataset that was either specified by a loader plugin or
                    created as output to a previous plugin.  The length of the
                    list is the number of input datasets requested by the
                    plugin.  If there is only one dataset and the list is left
                    empty it will default to that dataset.
            default: []

        out_datasets:
            visibility: datasets
            dtype: [list[str], list[]]
            description:
                summary: A list of the dataset(s) to create.
                verbose: >
                    A list of strings, where each string is a name to be
                    assigned to a dataset output by the plugin. If there is
                    only one input dataset and one output dataset and the list
                    is left empty, the output will take the name of the input
                    dataset. The length of the list is the number of output
                    datasets created by the plugin.
            default: []

        """
