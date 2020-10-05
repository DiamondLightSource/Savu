Nxfluo Loader
#################################################################

Description
--------------------------

A class to load tomography data from an NXFluo file.
    
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
        
        fluo_offset:
            visibility: basic
            dtype: float
            description: fluo scale offset.
            default: 0.0
        
        fluo_gain:
            visibility: intermediate
            dtype: float
            description: fluo gain
            default: 0.01
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: fluo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
