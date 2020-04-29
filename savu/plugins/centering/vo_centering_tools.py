from savu.plugins.plugin_tools import PluginTools
from savu.plugins.utils import register_plugin_tool

@register_plugin_tool
class VoCenteringTools(PluginTools):
    """A plugin to calculate the centre of rotation using the Vo Method
    """
    def define_parameters(self):
        """
        preview:
             visibility: basic
             dtype: '[int]'
             description: A slice list of required frames (sinograms) to use in
               the calculation of the centre of rotation (this will not reduce the data
               size for subsequent plugins).
             default: '[]'
        start_pixel:
             visibility: basic
             dtype: float
             description: The estimated centre of rotation. If value is None,
               use the horizontal centre of the image.
             default: 'None'
        search_area:
             visibility: basic
             dtype: float
             description: Search area around the estimated centre of rotation
             default: '(-50, 50)'
        ratio:
             visibility: basic
             dtype: float
             description: The ratio between the size of object and FOV of the camera
             default: 0.5
        search_radius:
             visibility: basic
             dtype: int
             description: Use for fine searching
             default: 6
        step:
             visibility: basic
             dtype: float
             description: Step of fine searching
             default: 0.5
        datasets_to_populate:
             visibility: advanced
             dtype: range
             description: A list of datasets which require this information
             default: '[]'
        out_datasets:
             visibility: advanced
             dtype: float
             description: The default names
             default: "['cor_preview','cor_broadcast']"
        broadcast_method:
             visibility: advanced
             dtype: str
             options: [median, mean, nearest, linear_fit]
             description:
               summary: Method of broadcasting centre values calculated
                 from preview slices to full dataset.
               options:
                   median:
                   mean:
                   nearest:
                   linear_fit:
             default: median
        row_drop:
             visibility: advanced
             dtype: int
             description: Drop lines around vertical center of the mask
             default: 20
        average_radius:
             visibility: advanced
             dtype: int
             description: Averaging sinograms around a required sinogram to
               improve signal-to-noise ratio
             default: 5
        """