Nxfluo Loader
#################################################################

Description
--------------------------

A class to load tomography data from an NXFluo file.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        fluo_offset:
            visibility: basic
            dtype: float
            description: fluo scale offset.
            default: 0.0
        fluo_gain:
            visibility: intermediate
            dtype: float
            description: fluo gain
            default: 0.01
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: fluo

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
