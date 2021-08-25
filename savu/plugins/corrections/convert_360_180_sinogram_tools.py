from savu.plugins.plugin_tools import PluginTools

class Convert360180SinogramTools(PluginTools):
    """Method to convert a 360-degree sinogram to a 180-degree sinogram in
    a half-acquisition scan.
    """
    def define_parameters(self):
        """
        center:
              visibility: basic
              dtype: float
              description: Center of rotation.
              default: 0.0
        out_datasets:
              visibility: intermediate
              dtype: [list[],list[str]]
              description: Create a list of the output datatsets to create.
              default: ['in_datasets[0]', 'cor']

        """