from savu.plugins.plugin_tools import PluginTools

class OrthoSliceTools(PluginTools):
    """A plugin to extract slices in each direction of a 3D reconstructed
    volume.
    """
    def define_parameters(self):
        """
        xy_slices:
            visibility: basic
            dtype: int
            description: which XY slices to render.
            default: 500

        yz_slices:
            visibility: basic
            dtype: int
            description: which YZ slices to render.
            default: 500

        xz_slices:
            visibility: basic
            dtype: int
            description: which XZ slices to render.
            default: 500

        file_type:
            visibility: basic
            dtype: str
            description: File type to save as
            default: 'png'

        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: Default out dataset names.
            default: "['XY','YZ','XZ']"
        """