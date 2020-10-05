Pymca
#################################################################

Description
--------------------------

Uses pymca to fit spectral data
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []
        
        config:
            visibility: intermediate
            dtype: config_file
            description: Path to the config file
            default: Savu/test_data/data/test_config.cfg
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
