from savu.plugins.plugin_tools import PluginTools

class BasicOperationsTools(PluginTools):
    """A class that performs basic mathematical operations on datasets.\
How should the information be passed to the plugin?
    """
    def define_parameters(self):
        """
        operations:
              visibility: basic
              dtype: list
              description: Operations to perform.
              default: []
        pattern:
              visibility: intermediate
              dtype: str
              description: Pattern associated with the datasets
              default: PROJECTION

        """