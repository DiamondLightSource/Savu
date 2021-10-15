from savu.plugins.plugin_tools import PluginTools

class UnetAggregateThreeTools(PluginTools):
    """
    A simple plugin template with one in_dataset and one out_dataset with
    similar characteristics, e.g. median filter.
    """

    def define_parameters(self):
        """
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: VOLUME_XZ
        """