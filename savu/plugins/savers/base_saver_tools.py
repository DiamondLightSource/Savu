from savu.plugins.plugin_tools import PluginTools

class BaseSaverTools(PluginTools):
    """A base plugin from which all data saver plugins should inherit.
    """
    def define_parameters(self):
        """
        out_datasets:
            visibility: hidden
            dtype: [list[],list[str]]
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