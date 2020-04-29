from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class RemoveAllRingsTools(PluginTools):
    """Method to remove all types of stripe artifacts in a sinogram (<-> ring artefacts
    in a reconstructed image).

    """
    def define_parameters(self):
        """
        la_size:
            visibility: param
            dtype: int
            description: Size of the median filter window to remove large stripes.
            default: 71
        sm_size:
            visibility: param
            dtype: int
            description: Size of the median filter window to remove small-to-medium stripes.
            default: 31
        snr:
            visibility: param
            dtype: float
            description: Ratio used to detect locations of stripes. Greater is less sensitive.
            default: 3.0
        """
