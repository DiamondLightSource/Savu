Random 3D Tomo Loader
########################################################

Description
--------------------------

A hdf5 dataset of a specified size is created at runtime using numpy random sampling (numpy.random), saved with relevant meta_data to a NeXus file, and used as input. It recreates the behaviour of the nxtomo loader but with random data.  The input file path passed to Savu will be ignored (use a dummy). Note: Further extensions planned to allow the generated data to be re-loaded with the nxtomo_loader. 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        size:
            visibility: basic
            dtype: "[list[float], list[]]"
            description: A list specifiying the required data size.
            default: "[]"
        
        axis_labels:
            visibility: basic
            dtype: "list[str]"
            description: A list of axis labels.
            default: "['rotation_angle.degrees', 'detector_y.angles', 'detector_x.angles']"
        
        patterns:
            visibility: hidden
            dtype: "list[str]"
            description: Patterns.
            default: "['SINOGRAM.0c.1s.2c', 'PROJECTION.0s.1c.2c']"
        
        file_name:
            visibility: intermediate
            dtype: str
            description: Assign a name to the created h5 file.
            default: input_array
        
        dtype_:
            visibility: intermediate
            dtype: nptype
            description: A numpy array data type
            default: int16
        
        dataset_name:
            visibility: hidden
            dtype: str
            description: The name assigned to the dataset.
            default: tomo
        
        angles:
            visibility: intermediate
            dtype: "[None,str,int]"
            description: "A python statement to be evaluated or a file - if the value is None, values will be in the interval [0, 180]"
            default: None
        
        pattern:
            visibility: intermediate
            dtype: "[None,str]"
            description: Pattern used to create and store the hdf5 dataset default is the first pattern in the pattern dictionary.
            default: None
        
        range:
            visibility: intermediate
            dtype: "list[float,float]"
            description: Set the distribution interval.
            default: "[1, 10]"
        
        image_key:
            visibility: intermediate
            dtype: list
            description: Specify position of darks and flats (in that order) in the data.
            default: "[[0, 1], [2, 3]]"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
