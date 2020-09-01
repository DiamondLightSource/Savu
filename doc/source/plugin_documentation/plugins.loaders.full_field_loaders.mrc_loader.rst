Mrc Loader
#################################################################

Description
--------------------------

Load Medical Research Council (MRC) formatted image data.
    
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
        
        angles:
            visibility: basic
            dtype: str
            description: A python statement to be evaluated (e.g np.linspace(0, 180, nAngles)) or a file.
            default: None
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset
            default: tomo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
