Ica
########################################################

Description
--------------------------

This plugin performs independent component analysis on XRD/XRF spectra. 

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
            description: A list of the dataset(s) to process.
            default: "['scores', 'eigenvectors']"
        
        number_of_components:
            visibility: basic
            dtype: int
            description: The number of expected components.
            default: "3"
        
        chunk:
            visibility: intermediate
            dtype: str
            description: The chunk to work on
            default: SINOGRAM
        
        whiten:
            visibility: intermediate
            dtype: int
            description: To subtract the mean or not.
            default: "1"
        
        w_init:
            visibility: basic
            dtype: "[None,list]"
            description: The initial mixing matrix.
            default: None
        
        random_state:
            visibility: intermediate
            dtype: int
            description: The state
            default: "1"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
