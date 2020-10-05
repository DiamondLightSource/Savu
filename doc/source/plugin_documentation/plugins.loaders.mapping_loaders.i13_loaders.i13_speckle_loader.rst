I13 Speckle Loader
#################################################################

Description
--------------------------

A class to load tomography data from an NXstxm file
    
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
        
        signal_key:
            visibility: basic
            dtype: float
            description: Path to the signals
            default: 9.1
        
        reference_key:
            visibility: intermediate
            dtype: int_path
            description: Path to the reference
            default: /entry/reference
        
        angle_key:
            visibility: intermediate
            dtype: int_path
            description: Path to the reference
            default: /entry/theta
        
        dataset_names:
            visibility: intermediate
            dtype: list
            description: The output sets.
            default: ['signal', 'reference']
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
