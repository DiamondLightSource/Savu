Xrd Absorption Approximation
########################################################

Description
--------------------------

McNears absorption correction, takes in a normalised absorption sinogram and xrd sinogram stack. A base absorption correction for stxm and xrd. 

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
        
        azimuthal_offset:
            visibility: intermediate
            dtype: int
            description: angle between detectors.
            default: "0"
        
        density:
            visibility: basic
            dtype: float
            description: The density
            default: "3.5377"
        
        compound:
            visibility: basic
            dtype: str
            description: The compound
            default: Co0.2(Al2O3)0.8
        
        log_me:
            visibility: intermediate
            dtype: bool
            description: should we log the transmission.
            default: "True"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
