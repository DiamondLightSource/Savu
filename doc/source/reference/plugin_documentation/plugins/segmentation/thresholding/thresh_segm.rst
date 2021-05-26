Thresh Segm
########################################################

Description
--------------------------

A Plugin to segment the data by providing two scalar values for lower and upper intensities 

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
        
        min_intensity:
            visibility: basic
            dtype: float
            description: A scalar to define lower limit for intensity, all values below are set to zero.
            default: "0"
        
        max_intensity:
            visibility: basic
            dtype: float
            description: A scalar to define upper limit for intensity, all values above are set to zero.
            default: "0.01"
        
        value:
            visibility: basic
            dtype: int
            description: An integer to set all values between min_intensity and max_intensity.
            default: "1"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: VOLUME_XY
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
