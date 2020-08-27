from savu.plugins.plugin_tools import PluginTools

class FinalSegmentI23Tools(PluginTools):
    """Apply at the end when all objects have been segmented independently (crystal, liquor, whole object)
    """
    def define_parameters(self):
        """
        set_classes_val:
            visibility: basic
            dtype: list
            description: 'Set the values for all 4 classes (crystal, liquor, loop, vacuum).'
            default: [255, 128, 64, 0]
        """
