List To Projections
########################################################

Description
--------------------------

Convert a list of points into a 2D projection 

Parameter definitions
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
        
        step_size_x:
            visibility: basic
            dtype: "[None,float]"
            description: step size in the interp, None if minimum chosen.
            default: None
        
        step_size_y:
            visibility: basic
            dtype: "[None,float]"
            description: step size in the interp, None if minimum chosen.
            default: None
        
        fill_value:
            visibility: basic
            dtype: "[int, str, float]"
            description: The value to fill with, takes an average if nothing else chosen.
            default: mean
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
