from savu.plugins.plugin_tools import PluginTools

class StxmAnalysisTools(PluginTools):
    """This plugin performs basic STXM analysis of diffraction patterns.
    """
    def define_parameters(self):
        """
        mask_file:
              visibility: basic
              dtype: [None,list]
              description: Takes in a mask currently in hdf format.
              default: None
        mask_path:
              visibility: intermediate
              dtype: h5path
              description: Path to the mask inside the file.
              default: '/mask'
        threshold:
              visibility: intermediate
              dtype: float
              description: Intensity threshold for the dark field.
              default: 0.05
        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description:
              default: ["bf","df","dpc_x","dpc_y","combined_dpc"]
        """