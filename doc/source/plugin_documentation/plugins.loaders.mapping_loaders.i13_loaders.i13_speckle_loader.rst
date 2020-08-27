I13 Speckle Loader
#################################################################

Description
--------------------------

A class to load tomography data from an NXstxm file
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        signal_key:
            visibility: basic
            dtype: float
            description: Path to the signals
            default: 9.1
        reference_key:
            visibility: intermediate
            dtype: int_path
            description: Path to the reference
            default: '/entry/reference'
        angle_key:
            visibility: intermediate
            dtype: int_path
            description: Path to the reference
            default: '/entry/theta'
        dataset_names:
            visibility: intermediate
            dtype: list
            description: The output sets.
            default: ['signal','reference']

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
