from savu.plugins.plugin_tools import PluginTools

class MonitorCorrectionTools(PluginTools):
    """Corrects the data to the monitor counts.
This plugin corrects data[0] from data[1] by dividing. We allow a scale
and offset due to I18's uncalibrated ic
    """
    def define_parameters(self):
        """
        in_datasets:
              visibility: datasets
              dtype: [list[],list[str]]
              description: A list of the dataset(s) to
                process.
              default: ['to_be_corrected','monitor']
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
              default: PROJECTION

        """