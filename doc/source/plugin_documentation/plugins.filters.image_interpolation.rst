Image Interpolation
#################################################################

Description
--------------------------

A plugin to interpolate an image by a factor
    
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
        
        size:
            visibility: basic
            dtype: ['int', 'float', 'tuple']
            description: int, float or tuple.
            default: 2.0
        
        interp:
            visibility: basic
            dtype: str
            description: nearest lanczos bilinear bicubic cubic.
            options: ['nearest', 'lanczos', 'bilinear', 'bicubic', 'cubic']
            default: bicubic
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
