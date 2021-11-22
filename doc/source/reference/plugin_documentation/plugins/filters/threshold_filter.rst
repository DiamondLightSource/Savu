Threshold Filter
########################################################

Description
--------------------------

A plugin to quantise an image into discrete levels. 

Parameters
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        explicit_threshold:
            visibility: basic
            dtype: bool
            description: "False if plugin calculates black/white threshold, True if it's user-defined."
            default: "True"
        
        intensity_threshold:
            visibility: basic
            dtype: int
            description: Threshold for black/white quantisation.
            default: "32768"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
