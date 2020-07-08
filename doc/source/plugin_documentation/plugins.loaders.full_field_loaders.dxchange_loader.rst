Dxchange Loader
#################################################################

Description
--------------------------

A class to load tomography data from a hdf5 file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        data_path:
            visibility: basic
            dtype: int_path
            description: Path to the data.
            default: 'exchange/data'
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
        logfile:
            visibility: intermediate
            dtype: filepath
            description: Path to the log file.
            default: None
        angles:
            visibility: hidden
            dtype: list
            description: Angles list
            default: '[1,2,3]'
        image_key_path:
            visibility: advanced
            dtype: int_path
            description: Not required.
            default: None

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
