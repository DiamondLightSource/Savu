Dxchange Loader
#################################################################

Description
--------------------------

A class to load tomography data from a hdf5 file
    
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
        
        name:
            visibility: basic
            dtype: str
            description: A name assigned to the dataset.
            default: tomo
        
        data_path:
            visibility: basic
            dtype: int_path
            description: Path to the data.
            default: exchange/data
        
        image_key_path:
            visibility: advanced
            dtype: int_path
            description: Not required.
            default: None
        
        dark:
            visibility: intermediate
            dtype: int_path_int
            description: Dark data path and scale
            default: "['exchange/data_dark', 1]"
        
        flat:
            visibility: intermediate
            dtype: int_path_int
            description: Flat data path and scale value.
            default: "['exchange/data_white', 1]"
        
        angles:
            visibility: hidden
            dtype: list
            description: Angles list
            default: "[1,2,3]"
        
        3d_to_4d:
            visibility: intermediate
            dtype: bool
            description: Many tomography datasets can be loaded. Value of True indicates the data must be reshaped.
            default: False
        
        ignore_flats:
            visibility: intermediate
            dtype: list
            description: List of batch numbers of flats to ignore (starting at 1). Useful for excluding comprimised flats in combined data sets containing multiple batches of interspaced flats. The batch indexing begins at 1.
            default: None
        
        logfile:
            visibility: intermediate
            dtype: filepath
            description: Path to the log file.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
