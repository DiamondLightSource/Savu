from savu.plugins.plugin_tools import PluginTools

class SavuNexusLoaderTools(PluginTools):
    """A class to load datasets, and associated metadata, from a Savu output
nexus file.

By default, the last instance of each unique dataset name will be loaded.
Opt instead to load a subset of these datasets, or individual datasets by
populating the parameters.

    """
    def define_parameters(self):
        """
        preview:
              visibility: basic
              dtype: list
              description: A slice list of required frames to apply to ALL
                datasets, else a dictionary of slice lists where the key is
                the dataset name.
              default: {}
        datasets:
              visibility: basic
              dtype: list
              description: Override the default by choosing specific
                dataset(s) to load, by stating the NXdata name.
              default: []
        names:
              visibility: basic
              dtype: list
              description: Override the dataset names associated with the
                datasets parameter above.
              default: []
        """