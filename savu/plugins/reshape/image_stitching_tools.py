from savu.plugins.plugin_tools import PluginTools

class ImageStitchingTools(PluginTools):
    """Method to stitch images of two tomo-datasets including
flat-field correction.
    """
    def define_parameters(self):
        """
        overlap:
            visibility: basic
            dtype: int
            description: Overlap width between two images.
            default: 354
        row_offset:
            visibility: basic
            dtype: int
            description: Offset of row indices of projections in the second
             dataset compared to the first dataset.
            default: -1
        crop:
            visibility: basic
            dtype: list[int,int,int,int]
            description: "Parameters used to crop stitched image with respect
              to the edges of an image. Format: [crop_top, crop_bottom,
              crop_left, crop_right]."
            default: [0, 0, 250, 250]
        pattern:
            visibility: intermediate
            dtype: str
            description: "Data processing pattern is 'PROJECTION' or
             'SINOGRAM'."
            default: 'PROJECTION'
        norm:
            visibility: intermediate
            dtype: bool
            description: Apply normalization before stitching.
            default: True
        flat_use:
            visibility: intermediate
            dtype: bool
            description: Apply flat-field correction.
            default: True
        """
