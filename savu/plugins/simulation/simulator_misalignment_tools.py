from savu.plugins.plugin_tools import PluginTools


class SimulatorMisalignmentTools(PluginTools):
    """A plugin to add x-y sub-pixel shifts to projections
    """

    def define_parameters(self):
        """
        shift_amplitude:
              visibility: basic
              dtype: float
              description: Define the maximum amplitude of x-y shifts for each projection
              default: 3.0

        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default input dataset names.
              default: "['synth_proj_data']"

        out_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: Default out dataset names.
              default: "['synth_proj_data_shifted']"
        """
