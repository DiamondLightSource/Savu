Convert 360 180 Sinogram
#################################################################

Description
--------------------------

Method to convert the 0-360 degree sinogram to 0-180 sinogram.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        center:
              visibility: intermediate
              dtype: float
              description: Center of rotation.
              default: 0.0
        out_datasets:
              visibility: intermediate
              dtype: list
              description: Create a list of the output datatsets to create.
              default: ['in_datasets[0]', 'cor']

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
