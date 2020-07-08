Sinogram Clean
#################################################################

Description
--------------------------

A plugin to calculate the centre of rotation using the Vo Method
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        ratio:
              visibility: basic
              dtype: float
              description:  The ratio between the size of object and FOV of
                the camera.
              default: 2.0
        row_drop:
              visibility: basic
              dtype: int
              description: 'Drop lines around vertical center of the mask
                scipy.optimize.curve_fit.'
              default: 20
        out_datasets:
              visibility: datasets
              dtype: list
              description: The default names.
              default: []

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
