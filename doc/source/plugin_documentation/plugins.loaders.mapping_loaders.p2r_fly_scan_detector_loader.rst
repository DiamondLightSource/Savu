P2R Fly Scan Detector Loader
#################################################################

Description
--------------------------

A class to load p2r fly scan detector data from a Nexus file.
    
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
        
        data_path:
            visibility: intermediate
            dtype: str
            description: Path to the data inside the file
            default: entry1/tomo_entry/data/data
        
        image_key_path:
            visibility: intermediate
            dtype: int_path
            description: Path to the image key entry inside the nxs file.
            default: entry1/tomo_entry/instrument/detector/image_key
        
        dark:
            visibility: intermediate
            dtype: file_int_path_int
            description: Optional path to the dark field data file, nxs path and              scale value.
            default: "[None, None, 1]"
        
        flat:
            visibility: intermediate
            dtype: file_int_path_int
            description: Optional path to the flat field data file, nxs path and              scale value.
            default: "[None, None, 1]"
        
        angles:
            visibility: intermediate
            dtype: str
            description: A python statement to be evaluated or a file.
            default: None
        
        3d_to_4d:
            visibility: intermediate
            dtype: bool
            description: Set to true if this reshape is required.
            default: False
        
        ignore_flats:
            visibility: intermediate
            dtype: list
            description: List of batch numbers of flats (start at 1) to              ignore.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
