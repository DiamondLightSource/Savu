Monitor Correction
########################################################

Description
--------------------------

Corrects the data to the monitor counts. This plugin corrects data[0] from data[1] by dividing. We allow a scale and offset due to I18's uncalibrated ic 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: A list of the dataset(s) to process.
            default: "['to_be_corrected', 'monitor']"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        nominator_scale:
            visibility: intermediate
            dtype: float
            description: a
            default: "1.0"
        
        nominator_offset:
            visibility: intermediate
            dtype: float
            description: b
            default: "0.0"
        
        denominator_scale:
            visibility: intermediate
            dtype: float
            description: c
            default: "1.0"
        
        denominator_offset:
            visibility: intermediate
            dtype: float
            description: d
            default: "0.0"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: The pattern to apply to it.
            default: PROJECTION
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
