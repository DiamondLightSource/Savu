I13 Stxm Xrf Loader
#################################################################

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
        
        preview:
            visibility: basic
            dtype: int_list
            description: A slice list of required frames.
            default: []
        
        data_file:
            visibility: hidden
            dtype: str
            description: hidden parameter for savu template
            default: <>
        
        is_map:
            visibility: basic
            dtype: bool
            description: Is it a map.
            default: True
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
