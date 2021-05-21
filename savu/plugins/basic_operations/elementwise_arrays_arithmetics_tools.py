from savu.plugins.plugin_tools import PluginTools

class ElementwiseArraysArithmeticsTools(PluginTools):
    """Basic arithmetic operations on two input datasets:
addition, subtraction, multiplication and division.

    """
    def define_parameters(self):
        """
        operation:
              visibility: basic
              dtype: str
              description: Arithmetic operation to apply to data, choose from addition, subtraction,
                multiplication and division.
              options: [addition, subtraction, multiplication, division]
              default: multiplication
        """