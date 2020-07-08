Developing a Savu plugin
************************

Each plugin performs a specific independent task, such as correction, \
filtering, reconstruction.  For a list of available plugins \
see :ref:`plugin documentation<plugin_documentation>`.

Plugins are grouped into categories of similar functionality.  Loaders and savers are two of these categories and each
process list must begin with a loader plugin and optionally end with a saver plugin (hdf5 is the default), with at
least one processing plugin in-between.  The loader informs the framework of the data location and format along
with important metadata such as shape, axis information, and associated patterns (e.g. sinogram, projection).
Therefore, the choice of loader is dependent upon the format of the data.

To create a plugin for Savu you will need to create two files:

1. plugin_name.py containing a class PluginName
2. plugin_name_tools.py containing a class PluginNameTools

PluginName should be replaced by the name of your plugin without \
any spaces. The words should be capitalised.

Examples are:

* AstraReconCpu
* RemoveAllRings
* TomobarRecon

1. Plugin Class
================

A docstring is a piece of text contained by three quotation marks """ \
<docstring_text> """. In the beginning docstring, write your plugin name \
and a short sentence to describe what it can do. This will later be shown to the user.

Docstring template:

.. code-block:: python

   """
    .. module:: <plugin_name>
       :platform: Unix
       :synopsis: <plugin_description>
    .. moduleauthor:: <author_name>

    """

Docstring example:

.. code-block:: python

   """
    .. module:: no_process
       :platform: Unix
       :synopsis: Plugin to test loading and saving without processing
    .. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

    """

Next, Import any classes which you may need. Normally you will require the \
Plugin class and the function decorator register_plugin.

Import example:

.. code-block:: python

    from savu.plugins.plugin import Plugin
    from savu.plugins.utils import register_plugin
    from savu.plugins.driver.cpu_plugin import CpuPlugin

Initialise the class template:

.. code-block:: python

    @register_plugin
    class PluginName(ParentPlugin):
        def __init__(self):
            super(PluginName, self).__init__("PluginName")

Initialise the class example:

.. code-block:: python

    @register_plugin
    class NoProcess(Plugin, CpuPlugin):
        def __init__(self):
            super(NoProcess, self).__init__("NoProcess")

Below is an example of the entire NoProcess plugin class.

Plugin Class example:

.. code-block:: python

    """
        .. module:: no_process
           :platform: Unix
           :synopsis: Plugin to test loading and saving without processing
        .. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

    """
    from savu.plugins.plugin import Plugin
    from savu.plugins.utils import register_plugin
    from savu.plugins.driver.cpu_plugin import CpuPlugin

    @register_plugin
    class NoProcess(Plugin, CpuPlugin):
        def __init__(self):
            super(NoProcess, self).__init__("NoProcess")

        def process_frames(self, data):
            return data[0]

        def setup(self):
            """
            Initial setup of all datasets required as input and output to the
            plugin.  This method is called before the process method in the plugin
            chain.
            """
            in_dataset, out_dataset = self.get_datasets()
            out_dataset[0].create_dataset(in_dataset[0])
            in_pData, out_pData = self.get_plugin_datasets()

            if self.parameters['pattern']:
                pattern = self.parameters['pattern']
            else:
                pattern = in_dataset[0].get_data_patterns().keys()[0]

            in_pData[0].plugin_data_setup(pattern, self.get_max_frames())
            out_pData[0].plugin_data_setup(pattern, self.get_max_frames())

        def get_max_frames(self):
            return 'multiple'

        def nInput_datasets(self):
            return 1

        def nOutput_datasets(self):
            return 1

2. Plugin Tools Class
======================

This tools class holds the parameter details in a yaml format.
To begin, import the PluginTools class.

.. code-block:: python

   from savu.plugins.plugin_tools import PluginTools

Beneath the class definition, write a docstring \
with a sentence to describe in further detail what your plugin does.

.. code-block:: python

    class NoProcessTools(PluginTools):
        """The base class from which all plugins should inherit.
        """
        def define_parameters(self):
            pass

Inside the function define_parameters you should write a docstring which will \
contain the parameter details. The text should be in a yaml format.

An example of a plugin tools class.

.. code-block:: python

    from savu.plugins.plugin_tools import PluginTools

    class NoProcessTools(PluginTools):
        """The base class from which all plugins should inherit.
        """
        def define_parameters(self):
            """---
            pattern:
                visibility: basic
                dtype: str
                description: Explicitly state the slicing pattern.
                default: None
            other:
                visibility: advanced
                dtype: int
                description: Temporary parameter for testing.
                default: 10
            yaml_file:
                visibility: advanced
                dtype: yaml_file
                description: Yaml file path.
                default: savu/plugins/loaders/full_field_loaders/nxtomo_loader.yaml

            """

Yaml Text
----------

.. code-block:: yaml

    pattern:
        visibility: advanced
        dtype: str
        description: Explicitly state the slicing pattern.
        default: None
    other:
        visibility: advanced
        dtype: int
        description: Temporary parameter for testing.
        default: 10
    yaml_file:
        visibility: advanced
        dtype: yaml_file
        description: Yaml file path.
        default: savu/plugins/loaders/full_field_loaders/nxtomo_loader.yaml

You should list the names of parameters required. After each name you \
need a colon. Then you include an indent and put four pieces of information: \
visibility, dtype, description, default.

These should contain:

* visibility - The level of understanding needed to edit the parameter
* dtype - The data type of the parameter value
* description - A description of the parameter
* default - A default value

Visibility
''''''''''
You should choose one of three options.

* basic - A basic parameter will need to be adjusted with each use of the plugin and will be on display to all users
* intermediate - An intermediate parameter can be used to tailor the plugin result more carefully.
* advanced - Advanced parameters should only need to be changed occasionally by developers.

Dtype
''''''

Choose the data type. This is used to check the parameter input is valid.

* [int]
* range
* yaml_file
* '[path, int_path, int]'
* '[path, int]'
* filepath
* directory
* int_path
* config_file
* filename
* nptype
* int
* bool
* str
* float
* tuple
* list

Description
'''''''''''
Any string of text

Default
'''''''
The default value of the parameter. For example, False, 0, 0.01

.. code-block:: yaml

    iterations:
        default: 0.01

This can be filled in with further details if this parameter is reliant on another.
For example, depending on the current value for the regularisation method, \
the default value for 'iterations' will change. When the method selected is \
ROF_TV, then the iterations value should be 1000.

.. code-block:: yaml

    iterations:
        default:
            regularisation_method:
                ROF_TV: 1000
                FGP_TV: 500
                PD_TV: 100
                SB_TV: 100
                LLT_ROF: 1000
                NDF: 1000
                DIFF4th: 1000

Optional fields:
----------------

Three additional fields may be included:

* dependency
* range
* options

Dependency
''''''''''

If the parameter is only applicable to certain other parameter choices \
you can make it only appear when a certain value is chosen.

For example, the NDF penalty should only be displayed when the regulartisation \
method is NDF.

.. code-block:: yaml

    NDF_penalty:
        dependency:
            regularisation_method: NDF

Options
'''''''

If you have a closed list of options for your parameter, you should enter \
them here. The case will not matter.

.. code-block:: yaml

    regularisation_method:
        options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF, Diff4th]

When you add options, you can include more fields within the description.

.. code-block:: yaml

    NDF_penalty:
        description:
           summary: Penalty dtype
           verbose: Nonlinear/Linear Diffusion model (NDF) specific penalty
             type.
           options:
             Huber: Huber
             Perona: Perona-Malik model
             Tukey: Tukey


Plugin Documentation
--------------------

.. toctree::
   :maxdepth: 2

   ../plugin_documentation


