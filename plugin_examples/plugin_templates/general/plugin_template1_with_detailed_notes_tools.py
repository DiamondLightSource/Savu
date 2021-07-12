from savu.plugins.plugin_tools import PluginTools

# Each plugin consists of two Python modules
#   - A plugin containing the processing
#   - A tools file containing the parameter and citation details


# Each plugin must have a complementary plugin file of the same name
# concatenated with "_tools.py"

class PluginTemplate1WithDetailedNotesTools(PluginTools):
    """
    A description of the plugin - the synopsis from the main plugin
    file appears as the short plugin description in the configurator
    and anything written here appears as the longer description (-vv flag).
    """

    def define_parameters(self):
        """
        example:
            visibility: basic
            dtype: [None, str]
            description: Example of a plugin parameter
            default: None

        """