from savu.plugins.plugin_tools import PluginTools

class DownsampleFilterTools(PluginTools):
    """A plugin to downsample and rescale data volume including options of
    flipping and rotating images
    """
    def define_parameters(self):
        """
        bin_size:
            visibility: basic
            dtype: int
            description: Bin Size for the downsample.
            default: 3
        mode:
            visibility: basic
            dtype: str
            description: One of 'mean', 'median', 'min', 'max'.
            default: mean
            options: [mean,median,min,max]
        pattern:
            visibility: basic
            dtype: str
            description: One of 'PROJECTION' or 'SINOGRAM' or 'VOLUME_XZ'.
            default: PROJECTION
            options: ['PROJECTION', 'SINOGRAM', 'VOLUME_XZ']
        num_bit:
            visibility: basic
            dtype: int
            description: Bit depth of the rescaled data (8, 16 or 32).
            default: 32
            options: [8,16,32]
        flip_updown:
            visibility: basic
            dtype: bool
            description: Flip images up-down.
            default: True
        flip_leftright:
            visibility: basic
            dtype: bool
            description: Flip images left-right.
            default: False
        rotate_angle:
            visibility: basic
            dtype: [float, str, list[float], dict{int:float}]
            description: Rotate images by a given angle (Degree).
            default: 0.0
        max:
            visibility: basic
            dtype: [None,float]
            description: Global max for scaling.
            default: None
        min:
            visibility: basic
            dtype: [None,float]
            description: Global min for scaling.
            default: None

        """

