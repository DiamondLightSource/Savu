from savu.plugins.plugin_tools import PluginTools

class Rotate90Tools(PluginTools):
    """A plugin to rotate an image 90 degrees clockwise or anticlockwise."""
    
    def define_parameters(self):
        """
        direction:
            visibility: basic
            dtype: str
            description: Direction for the 90 degree rotation. CW (clockwise) or ACW (anti-clockwise)
            default: ACW
            options: [ACW, CW]

        pattern:
             visibility: intermediate
             dtype: str
             options: [PROJECTION, SINOGRAM, VOLUME_XZ]
             description: Pattern to apply this to.
             default: PROJECTION

        """
