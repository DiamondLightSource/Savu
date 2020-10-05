List To Projections
#################################################################

Description
--------------------------

Converts a list of points into a 2D projection
    
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
        
        step_size_x:
            visibility: basic
            dtype: int
            description: step size in the interp, None if minimum chosen.
            default: None
        
        step_size_y:
            visibility: basic
            dtype: int
            description: step size in the interp, None if minimum chosen.
            default: None
        
        fill_value:
            visibility: basic
            dtype: ['int', 'str', 'float']
            description: The value to fill with, takes an average if nothing else chosen.
            default: mean
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
