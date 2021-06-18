from savu.plugins.plugin_tools import PluginTools

class BasicOperationsTools(PluginTools):
    """A class that performs basic mathematical operations on datasets.
    """

    def define_parameters(self):
        """
        operations:
              visibility: basic
              dtype: [list[],list[str]]
              description: Operations to perform.
              default: []
        pattern:
              visibility: intermediate
              dtype: str
              description: Pattern associated with the datasets
              default: PROJECTION
        """
