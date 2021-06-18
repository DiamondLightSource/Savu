from savu.plugins.plugin_tools import PluginTools

class MonitorCorrectionNdTools(PluginTools):
    """
    Corrects the data to the monitor counts.
    """

    def define_parameters(self):
        """
        in_datasets:
              visibility: datasets
              dtype: list
              description: "A list of the dataset(s) to
                process."
              default: "['to_be_corrected', 'monitor']"

        nominator_scale:
              visibility: intermediate
              dtype: float
              description: a
              default: 1.0

        nominator_offset:
              visibility: intermediate
              dtype: float
              description: b
              default: 0.0

        denominator_scale:
              visibility: intermediate
              dtype: float
              description: c
              default: 1.0

        denominator_offset:
              visibility: intermediate
              dtype: float
              description: d
              default: 0.0

        pattern:
              visibility: intermediate
              dtype: str
              description: The pattern to apply to it.
              default: 'SPECTRUM'

        monitor_pattern:
              visibility: intermediate
              dtype: str
              description: The pattern to apply to it.
              default: 'CHANNEL'

        """