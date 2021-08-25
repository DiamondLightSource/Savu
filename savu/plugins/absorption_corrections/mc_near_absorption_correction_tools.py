from savu.plugins.plugin_tools import PluginTools

class McNearAbsorptionCorrectionTools(PluginTools):
    """McNears absorption correction, takes in a normalised absorption sinogram
and xrf sinogram stack.
    """
    def define_parameters(self):
        """
        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: "A list of the dataset(s) to process."
              default: ['xrf','stxm']
        """
