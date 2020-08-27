Median Filter
#################################################################

Description
--------------------------

A plugin to filter each frame with a 3x3 median filter.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        kernel_size:
             visibility: basic
             dtype: tuple
             description: Kernel size for the filter.
             default: (1, 3, 3)

        pattern:
             visibility: advanced
             dtype: str
             description: Pattern to apply this to.
             default: PROJECTION

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
