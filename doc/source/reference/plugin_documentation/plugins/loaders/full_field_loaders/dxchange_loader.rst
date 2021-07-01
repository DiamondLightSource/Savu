Dxchange Loader
########################################################

Description
--------------------------

A class to load tomography data from a hdf5 file 

Parameter definitions
--------------------------

.. code-block:: yaml

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
            visibility: hidden
            dtype: None
            description: Not required.
            default: None
        
        dark:
            visibility: basic
            dtype: "list[h5path, float]"
            description: Hdf path to the dark-field data and scale.
            default: "['exchange/data_dark', 1.0]"
        
        flat:
            visibility: basic
            dtype: "list[h5path, float]"
            description: Hdf path to the flat-field data and scale.
            default: "['exchange/data_white', 1.0]"
        
        angles:
            visibility: basic
            dtype: h5path
            description: Hdf path to the angle data.
            default: exchange/theta
        
        3d_to_4d:
            visibility: intermediate
            dtype: "[bool, int]"
            description: If this is 4D data stored in 3D then set this value to True, or to an integer value equivalent to the number of projections per 180-degree scan if the angles have not been set.
            default: "False"
        
        ignore_flats:
            visibility: intermediate
            dtype: "[list[int], None]"
            description: List of batch numbers of flats to ignore (starting at 1). Useful for excluding comprimised flats in combined data sets containing multiple batches of interspaced flats. The batch indexing begins at 1.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
