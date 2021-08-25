from savu.plugins.plugin_tools import PluginTools

class ArithmeticOperationsTools(PluginTools):
    """
    Basic arithmetic operations on data: addition, subtraction, multiplication
    and division. Operations can be performed by extracting scalars from
    METADATA (min, max, mean) OR providing a scalar value.
    """

    def define_parameters(self):
        """
        scalar_value:
              visibility: basic
              dtype: [None,float]
              description: A scalar value value for arithmetic operation
               (if not in metadata).
              default: None

        operation:
              visibility: basic
              dtype: str
              description: Arithmetic operation to apply to data
              options: [addition, subtraction, multiplication, division]
              default: division

        metadata_value:
              visibility: basic
              dtype: str
              description: A type of scalar extracted from metadata
               (min, max, mean).
              default: max
              options: [min, max, mean]
        """