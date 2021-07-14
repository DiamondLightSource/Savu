from savu.plugins.plugin_tools import PluginTools

class DataThresholdTools(PluginTools):
    """The module to threshold the data (less, lessequal, equal, greater,
greaterequal) than the given value, based on the condition the data values
will be replaced by the provided new value

    """
    def define_parameters(self):
        """
        inequality_condition:
              visibility: basic
              dtype: str
              description: Set to less, lessequal, equal, greater, greaterequal
              options: [less, lessequal, equal, greater, greaterequal]
              default: greater
        given_value:
              visibility: basic
              dtype: int
              description: The value to be replaced with by inequality_condition.
              default: 1
        new_value:
              visibility: basic
              dtype: int
              description: The new value.
              default: 1
        pattern:
            visibility: advanced
            dtype: str
            options: [SINOGRAM, PROJECTION, VOLUME_XZ, VOLUME_YZ]
            description: Pattern to apply this to.
            default: 'VOLUME_XZ' 

        """
