from savu.plugins.plugin_tools import PluginTools

class VoCenteringTools(PluginTools):
    """A plugin to calculate the centre of rotation using the Vo Method
    """
    def define_parameters(self):
        """---
        preview:
             visibility: user
             dtype: '[int]'
             description: A slice list of required frames (sinograms) to use in
               the calculation of the centre of rotation (this will not reduce the data
               size for subsequent plugins).
             default: '[]'
        start_pixel:
             visibility: user
             dtype: float
             description: The estimated centre of rotation. If value is None,
               use the horizontal centre of the image.
             default: 'None'
        search_area:
             visibility: user
             dtype: float
             description: Search area around the estimated centre of rotation
             default: '(-50, 50)'
        ratio:
             visibility: user
             dtype: float
             description: The ratio between the size of object and FOV of the camera
             default: 0.5
        search_radius:
             visibility: user
             dtype: int
             description: Use for fine searching
             default: 6
        step:
             visibility: user
             dtype: float
             description: Step of fine searching
             default: 0.5
        datasets_to_populate:
             visibility: param
             dtype: range
             description: A list of datasets which require this information
             default: '[]'
        out_datasets:
             visibility: param
             dtype: float
             description: The default names
             default: "['cor_preview','cor_broadcast']"
        broadcast_method:
             visibility: param
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
             visibility: param
             dtype: int
             description: Drop lines around vertical center of the mask
             default: 20
        average_radius:
             visibility: param
             dtype: int
             description: Averaging sinograms around a required sinogram to
               improve signal-to-noise ratio
             default: 5
        """