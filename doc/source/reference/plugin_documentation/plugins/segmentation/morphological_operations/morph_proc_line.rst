Morph Proc Line
########################################################

Description
--------------------------

A Larix morphological processing module using line segments to remove inconsistent gaps 

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
        
        primeclass:
            visibility: basic
            dtype: int
            description: a mask class to start morphological processing from.
            default: "0"
        
        correction_window:
            visibility: intermediate
            dtype: int
            description: the size of the correction window.
            default: "7"
        
        iterations:
            visibility: basic
            dtype: int
            description: the number of iterations for segmentation.
            default: "15"
        
        pattern:
            visibility: basic
            dtype: str
            description: Pattern to apply this to.
            default: VOLUME_YZ
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
