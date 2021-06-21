from savu.plugins.plugin_tools import PluginTools

class ForwardProjectorGpuTools(PluginTools):
    """This plugin uses ToMoBAR software and GPU Astra projector to generate parallel-beam projection data.
The plugin will project the given object using the available metadata OR user-provided geometry.
In case when angles set to None, the metadata projection geometry will be used.
    """
    def define_parameters(self):
        """
        angles_deg:
            visibility: advanced
            dtype: [None, list[float,float,int]]
            description: Projection angles in degrees in a format [start, stop, total number of angles].
            default: None

        det_horiz:
            visibility: advanced
            dtype: int
            description: The size of the horizontal detector.
            default: None

        centre_of_rotation:
            visibility: advanced
            dtype: float
            description: The centre of rotation.
            default: None

        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: The default names
            default: ['forw_proj']
        """
