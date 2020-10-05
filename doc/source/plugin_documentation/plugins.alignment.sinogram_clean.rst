Sinogram Clean
#################################################################

Description
--------------------------

A plugin to calculate the centre of rotation using the Vo Method
    
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
            description: The default names.
            default: []
        
        ratio:
            visibility: basic
            dtype: float
            description: The ratio between the size of object and FOV of the camera.
            default: 2.0
        
        row_drop:
            visibility: basic
            dtype: int
            description: Drop lines around vertical center of the mask scipy.optimize.curve_fit.
            default: 20
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
