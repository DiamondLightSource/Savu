Region Grow3D
########################################################

Description
--------------------------

Fast 3D segmentation by evolving the user-given mask, the initialised mask should be set in the central part of the object to be segmented. 

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
            description: The default names
            default: "['MASK_RG_EVOLVED']"
        
        threshold:
            visibility: basic
            dtype: float
            description: parameter to control mask propagation.
            default: "1.0"
        
        method:
            visibility: intermediate
            dtype: str
            description: a method to collect statistics from the given mask (mean, median, value).
            default: mean
        
        iterations:
            visibility: basic
            dtype: int
            description: number of iterations.
            default: "500"
        
        connectivity:
            visibility: intermediate
            dtype: int
            description: the connectivity of the local neighbourhood, choose 4, 6, 8 or 26.
            default: "6"
            options: "[4, 6, 8, 26]"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
