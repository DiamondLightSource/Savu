Image Loader
#################################################################

Description
--------------------------

Load any FabIO compatible formats (e.g. tiffs)
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        dataset_name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        angles:
            visibility: intermediate
            dtype: str
            description: 'A python statement to be evaluated
              (e.g np.linspace(0, 180, nAngles)) or a file.'
            default: None
        frame_dim:
            visibility: intermediate
            dtype: int
            description: Which dimension requires stitching?
            default: None
        data_prefix:
            visibility: intermediate
            dtype: str
            description: A file prefix for the data file.
            default: None
        dark_prefix:
            visibility: intermediate
            dtype: str
            description: A file prefix for the dark field files, including the              folder path if different from the data.
            default: None
        flat_prefix:
            visibility: intermediate
            dtype: str
            description: A file prefix for the flat field files, including the              folder path if different from the data.
            default: None

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
