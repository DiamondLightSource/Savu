Spectrum Crop
#################################################################

Description
--------------------------

Crops a spectrum to a range
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        crop_range:
              visibility: intermediate
              dtype: list
              description: Range to crop to.
              default: [2., 18.]
        axis:
              visibility: intermediate
              dtype: str
              description: Axis.
              default: energy

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
