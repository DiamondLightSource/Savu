.. _plugin_guide:

.. raw:: html

    <style> .blue {color:#2c7aa3} </style>

.. role:: blue

How to develop a Savu plugin
******************************

The architecture of the savu package is that new plugins can be easily developed
without having to take the framework into consideration.  This is mostly true for
simple cases, however there are some things which cannot be done with such
simple methodologies and the developer may need to take more into consideration.

Every plugin in Savu needs to be a subclass of the Plugin class, however there
are several convenience subclasses which already exist for doing standard
processes such as filtering, reconstruction and augmentation/passthrough

Although there are many plugins defined in the core savu code, plugins can be
written anywhere and included easily as shown below without having to be submitted
to the core code.

Required Files
=======================

To create a plugin for Savu you will need to create two modules:

1. A plugin module, named :blue:`plugin_name`.py containing a class :blue:`PluginName`

    This file contains your plugin definitions and statements.

2. A plugin tools module named :blue:`plugin_name_tools`.py, containing a class :blue:`PluginNameTools`

    This file contains the parameter details and citations in a yaml format. You can \
    assign each parameter a data type, a description, a visibility level and a \
    default value.

.. note::

    A module is a file containing python definitions and statements.

.. note::

    :blue:`PluginName` should be replaced by the name of your plugin without \
    any spaces. The words should be capitalised. :blue:`plugin_name` should be
    replaced by the name of your plugin in lowercase, seperated by underscores.

Examples are:

* 1. A plugin module astra_recon_cpu.py containing a class AstraReconCpu
  2. A plugin tools module astra_recon_cpu_tools.py containing a class AstraReconCpuTools

* 1. A plugin module remove_all_rings.py containing a class RemoveAllRings
  2. A plugin tools module remove_all_rings_tools.py containing a class RemoveAllRingsTools

The plugin file and the plugin tools file should both be stored at the same directory inside ../Savu/savu/plugins/.

1. Introduction to creating a Plugin
========================================

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

Below is the template plugin class.

.. literalinclude:: ../files_and_images/plugin_guides/plugin_name_example.py
    :language: python

You can download it :download:`here <../files_and_images/plugin_guides/plugin_name_example.py>`.
An extended version is available :download:`here <../../../plugin_examples/plugin_templates/general/plugin_template1_with_detailed_notes.py>`.

All template downloads are available here: :ref:`plugin_templates`.

Below is an example of the entire NoProcess plugin class.

Plugin Class example:

.. TODO insert raw code in place of text

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

.. _toolclassguide:

2. How to create the tools class and documentation
===================================================

This tools class holds the parameter details in a yaml format.
There is advice on this format :ref:`here<yaml_format>`.
To begin, import the PluginTools class.

.. code-block:: python

   from savu.plugins.plugin_tools import PluginTools

Beneath the class definition, write a docstring \
with a sentence to describe in further detail what your plugin does.

.. code-block:: python

    class NoProcessTools(PluginTools):
        """The base class from which all plugins should inherit.
        """

Inside the method define_parameters you should write a docstring which will \
contain the parameter details. The text should be in a :ref:`yaml<yaml_format>` format.

An example of a plugin tools class.

.. code-block:: python

    from savu.plugins.plugin_tools import PluginTools

    class NoProcessTools(PluginTools):
        """The base class from which all plugins should inherit.
        """
        def define_parameters(self):
            """
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

You should list the names of parameters required. After each name you
need a colon. Then you include an indent and put four pieces of information:
visibility, dtype, description, default. The indentation level should be
consistent.

The parameter information included should be:

* visibility - There are five visibility levels. The level helps the user to identify which parameters must be changed on every savu run and which need to be changed less frequently.
* dtype - The data type of the parameter value
* description - A description of the parameter
* default - A default value

Visibility
''''''''''
You should choose one of five options.

* basic - A basic parameter will need to be adjusted with each use of the plugin and will be on display to all users as default.
* intermediate - An intermediate parameter can be used to tailor the plugin result more carefully.
* advanced - Advanced parameters should only need to be changed occasionally by developers.
* datasets - This is used for the in_datasets and out_datasets parameter only.
* hidden - Hidden parameters are not editable from the user interface. This may be useful during plugin development.

Dtype
''''''

Choose the data type. This is used to check the parameter input is valid.

.. list-table::
    :header-rows: 1
    :widths: 50 50

    * - Data Type
      - Description
    * - int
      - An integer
    * - pos_int
      - A positive integer
    * - bool
      - A boolean
    * - str
      - A string
    * - float
      - A float
    * - tuple
      - A tuple
    * - list
      - A list
    * - int_list
      - A list of integers
    * - string_list
      - A list of strings
    * - num_list
      - A list of numbers
    * - empty_list
      - An empty list
    * - preview
      - Preview slice list
    * - range
      - A range e.g. (0,1)
    * - yaml_file
      - A yaml file
    * - file_int_path_int
      - A sequence of items. The first item in the list should be a
        file path, the next should be an interior file path, the last
        item should be an integer. [<file path>, <interior path>, <integer>]
    * - int_path_int
      - A sequence of items. The first item in the list should be an
        interior file path, the last item should be an integer.
        [<interior path> , <integer>]
    * - filepath
      - A file path
    * - savufilepath
      - A file path within the Savu directory
    * - directory
      - A file directory
    * - int_path
      - An interior path
    * - config_file
      - A configuration file
    * - filename
      - A file name
    * - nptype
      - A numpy type
    * - dict
      - A dictionary
    * - int_float_dict
      - A dictionary holding ineteger keys and float values. {int:float}


If more than one data type is allowed, then include these in a list format.
e.g. [int, float] would mean that integers or floats are valid data types.

If you are a developer and would like to create your own data type then you
should edit the file parameter_utils.py. This file is inside the directory
Savu/scripts/config_generator/.

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
For example, depending on the current value for the regularisation method,
the default value for 'iterations' will change. When the method selected is
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

Additional fields whaich may be included:

* dependency
* options

and additional fields which should be included within the description key are:

* summary
* verbose
* range
* options


Dependency
''''''''''

If the parameter is only applicable to certain other parameter choices
you can make it only appear when a certain value is chosen.

For example, the NDF penalty should only be displayed when the regularisation
method is NDF.

.. code-block:: yaml

    NDF_penalty:
        dependency:
            regularisation_method: NDF

If you want this parameter to appear when the value is not a None value,
you can type the string 'not None'.

Options
'''''''

If you have a closed list of options for your parameter, you should enter
them here. The case will matter.

.. code-block:: yaml

    regularisation_method:
        options: [ROF_TV, FGP_TV, PD_TV, SB_TV, LLT_ROF, NDF, Diff4th]

When you add options, you can include more fields within the description.
The indentation level should be consistent.

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

Description
'''''''''''''

If you are giving a more detailed description, then you can extend the description key.
Summary, verbose, range, and options descriptions can be included here.


Summary
:::::::::

The summary holds a short description of your parameter.

.. code-block:: yaml

    data_Huber_thresh:
        description:
            summary: Threshold parameter for Huber data fidelity.


Verbose
::::::::

Verbose is for a more in depth explanation of your parameter.

.. code-block:: yaml

    data_Huber_thresh:
        description:
            summary: Threshold parameter for Huber data fidelity.
            verbose: Parameter which controls the level of suppression
             of outliers in the data

Range
::::::

If you have a value which must be within a certain range, describe this range here.

Range is a descriptor key at the moment, and it does not perform a validation check.

.. code-block:: yaml

    iteration:
        description:
            range: Between 10 and 100


Citation Text
--------------

The citations are included inside the method define_citations. You should
write a docstring which will contain the citation details. The text should
be in a yaml format.

.. code-block:: python

    from savu.plugins.plugin_tools import PluginTools

    class NoProcessTools(PluginTools):
        """The base class from which all plugins should inherit.
        """
        def define_parameters(self):
            """
            """
        def citation(self):
            """
            Short description
            bibtex:
                    Bibtex block of text.
            endnote:
                    Endnote block of text.
            doi: doi link
            """
        def citation2(self):
            """
            Short description
            bibtex:
                    Bibtex block of text.
            endnote:
                    Endnote block of text.
            doi: doi link
            """

If unicode characters are included, for example the character mew, you can
precede the docstring with the letter 'u'.

.. code-block:: python

        def define_citations(self):
            u"""
            The Tomographic filtering performed in this processing
            chain is derived from this work.
            bibtex:
                    @article{price2015chemical,
                    title={Chemical imaging of single catalyst particles with scanning $\mu$-XANES-CT and $\mu$-XRF-CT},
                    author={Price, SWT and Ignatyev, K and Geraki, K and Basham, M and Filik, J and Vo, NT and Witte, PT and Beale, AM and Mosselmans, JFW},
                    journal={Physical Chemistry Chemical Physics},
                    volume={17},
                    number={1},
                    pages={521--529},
                    year={2015},
                    publisher={Royal Society of Chemistry}}
            endnote:
                    %0 Journal Article
                    %T Chemical imaging of single catalyst particles with scanning \u03BC-XANES-CT and \u03BC-XRF-CT
                    %A Price, SWT
                    %A Ignatyev, K
                    %A Geraki, K
                    %A Basham, M
                    %A Filik, J
                    %A Vo, NT
                    %A Witte, PT
                    %A Beale, AM
                    %A Mosselmans, JFW
                    %J Physical Chemistry Chemical Physics
                    %V 17
                    %N 1
                    %P 521-529
                    %D 2015
                    %I Royal Society of Chemistry
            doi: "10.1039/c4cp04488f"

            """

Below is a longer example of the yaml text.

.. code-block:: none

        The CCPi-Regularisation toolkit provides a set of
        variational regularisers (denoisers) which can be embedded in
        a plug-and-play fashion into proximal splitting methods for
        image reconstruction. CCPi-RGL comes with algorithms that can
        satisfy various prior expectations of the reconstructed object,
        for example being piecewise-constant or piecewise-smooth nature.
        bibtex:
                @article{kazantsev2019ccpi,
                title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
                author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
                journal={SoftwareX},
                volume={9},
                pages={317--323},
                year={2019},
                publisher={Elsevier}
                }
        endnote:
                %0 Journal Article
                %T Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms
                %A Kazantsev, Daniil
                %A Pasca, Edoardo
                %A Turner, Martin J
                %A Withers, Philip J
                %J SoftwareX
                %V 9
                %P 317-323
                %@ 2352-7110
                %D 2019
                %I Elsevier
        short_name_article: ccpi regularisation toolkit for CT
        doi: "10.1016/j.softx.2019.04.003"


Description
''''''''''''

This is a string describing the citation.


.. code-block:: yaml

    description: A string to describe the citation


Bibtex
''''''''''

The bibtex text.

.. code-block:: none

    bibtex:
            @article{kazantsev2019ccpi,
            title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
            author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
            journal={SoftwareX},
            volume={9},
            pages={317--323},
            year={2019},
            publisher={Elsevier}
            }

Endnote
''''''''''

The endnote text.

.. code-block:: none

    endnote:
            @article{kazantsev2019ccpi,
            title={Ccpi-regularisation toolkit for computed tomographic image reconstruction with proximal splitting algorithms},
            author={Kazantsev, Daniil and Pasca, Edoardo and Turner, Martin J and Withers, Philip J},
            journal={SoftwareX},
            volume={9},
            pages={317--323},
            year={2019},
            publisher={Elsevier}
            }

Digital Object Identifier
'''''''''''''''''''''''''''

The DOI identifies a journal or article. It should remain fixed over
the lifetime of the journal. It is a character string divided into two
parts, a prefix and a suffix, separated by a slash.

.. code-block:: yaml

    doi: "10.1016/0167-2789(92)90242-F"

Dependency
''''''''''

If the citation is only applicable to certain other parameter choices
you can make it only appear when a certain value is chosen.

For example, the ROF_TV citation should only be displayed when the
method is ROF_TV.

.. code-block:: yaml

    dependency:
        method: ROF_TV


Document your plugin in restructured text
-------------------------------------------


If you are creating your plugin with the :ref:`'savu_plugin_generator'<plugin_generator_guide>` command, then
the restructured text file will be created automatically for you and the
link to this file will be printed to the terminal window.

You will need to open the linked file and write down instructions about
how to use your plugin. The language this file should be written in is
reStructured text. This is described in more detail here:
https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

An example would be:

.. literalinclude:: ../files_and_images/plugin_guides/plugin_name_doc.rst
   :language: rst
   :start-after: :orphan:


Plugin Documentation
--------------------

Below is a list of the current plugins grouped by type. You may also use the
search bar on the left to find a specific one.

.. toctree::
   :maxdepth: 2

   ../reference/plugin_documentation


3. How to create a test
============================================


Testing something else in line with text example_

In order to submit a new plugin to Savu on Github, you **MUST** provide a test for your new plugin.
To create a test follow the steps below:

    1. Choose a `test template`_
    2. Choose a `test dataset`_
    3. `Amend the parameters`_ r1,...,r8 in the file.
    4. Save the file.
    5. Add the file to your local repository.

.. _`test template`:

Test templates
------------------

If your plugin is not dependent on any others (i.e. it can be run on its own on raw or corrected data), then
download the :download:`sample test WITHOUT a process list<../files_and_images/example_test.py>`. This will test
the plugin with default parameters.

If your plugin is dependent on other plugins, you will need to create a process list **create a process list link**
and download the :download:`sample test WITH a process list <../files_and_images/example_test_with_process_list.py>`.


.. _`test dataset`:

Test data
------------

List of test data available.
What to do if you require different test data.
You can submit a new test dataset to Savu, with the requirement that it is less than 10MB in size.


.. _`Amend the parameters`:

Amending the parameters
-------------------------

See the real test modules:
    1. :download:`median_filter_test.py <../files_and_images/median_filter_test.py>` tests the median_filter_plugin.py plugin **WITH NO PROCESS LIST**.
    2. :download:`median_filter_test.py <../files_and_images/median_filter_test.py>` tests the median_filter_plugin.py plugin **WITH NO PROCESS LIST**.


Save the file as "your_module_name.py"

.. warning:: Ensure the test file name has the same name as the module name (r1)

.. note:: Have a look at the :download:`real test <../files_and_images/median_filter_test.py>` for the median_filter_plugin.py module.


..
    Median Filter Example
    ---------------------

    This examples recreates one of the core plugins, a median filter.  The code is
    available in the main Savu repository under the plugin_examples folder.

    .. literalinclude:: ../../../plugin_examples/example_median_filter.py
       :linenos:

    As you can see this is a pretty small implementation, and the key features of
    which are detailed in the comments associated with the code.

..
    Testing the new plugin
    ======================

    So now that you have the new plugin written, you can test it using the following
    command, you will need to make sure that savu is installed or included in your
    $PYTHON_PATH

    .. code:: bash

       python $SAVU_HOME/savu/test/framework_test.py -p $SAVU_HOME/plugin_examples/example_median_filter /tmp/savu_output/
