Dxchange Loader
########################################################

Description
--------------------------

A class to load tomography data from a hdf5 file 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: not
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s) to process
            default: "[]"
        
        out_datasets:
            visibility: not
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s) to create
            default: "[]"
        
        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        name:
            visibility: intermediate
            dtype: str
            description: A name assigned to the dataset.
            default: tomo
        
        data_path:
            visibility: basic
            dtype: h5path
            description: Path to the data.
            default: exchange/data
        
        image_key_path:
            visibility: advanced
            dtype: "[None,h5path]"
            description: Not required.
            default: None
        
        dark:
            visibility: intermediate
            dtype: "list[[h5path, None], float]"
            description: Dark data path and scale
            default: "['exchange/data_dark', 1]"
        
        flat:
            visibility: intermediate
            dtype: "list[[h5path, None], float]"
            description: Flat data path and scale value.
            default: "['exchange/data_white', 1]"
        
        angles:
            visibility: hidden
            dtype: list
            description: Angles list
            default: "[1, 2, 3]"
        
        3d_to_4d:
            visibility: intermediate
            dtype: bool
            description: Many tomography datasets can be loaded. Value of True indicates the data must be reshaped.
            default: "False"
        
        ignore_flats:
            visibility: intermediate
            dtype: "[list[int], None]"
            description: List of batch numbers of flats to ignore (starting at 1). Useful for excluding comprimised flats in combined data sets containing multiple batches of interspaced flats. The batch indexing begins at 1.
            default: None
        
        logfile:
            visibility: intermediate
            dtype: "[None,filepath]"
            description: Path to the log file.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
