Merge Binary Mask 3D
#################################################################

Description
--------------------------

A plugin to remove gaps in the provided binary mask by merging the boundaries
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        primeclass:
            visibility: basic
            dtype: list
            description: Class to start morphological processing from.
            default: 0

        correction_window:
            visibility: intermediate
            dtype: int
            description: The size of the correction window.
            default: 7

        iterations:
            visibility: intermediate
            dtype: int
            description: The number of iterations for segmentation.
            default: 3

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
