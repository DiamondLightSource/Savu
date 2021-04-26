from savu.plugins.plugin_tools import PluginTools

class Convert360180SinogramTools(PluginTools):
    """Method to convert the 0-360 degree sinogram to 0-180 sinogram.
    """
    def define_parameters(self):
        """
        center:
              visibility: intermediate
              dtype: float
              description: Center of rotation.
              default: 0.0
        out_datasets:
              visibility: intermediate
              dtype: [list[],list[str]]
              description: Create a list of the output datatsets to create.
              default: ['in_datasets[0]', 'cor']

        """