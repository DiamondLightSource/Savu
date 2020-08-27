Quantisation Filter
#################################################################

Description
--------------------------

A plugin to quantise an image into discrete levels.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        explicit_min_max:
              visibility: intermediate
              dtype: bool
              description: "False if min/max intensity comes from the
                metadata, True if it's user-defined. "
              default: False
        min_intensity:
              visibility: intermediate
              dtype: int
              description: Global minimum intensity.
              default: 0
        max_intensity:
              visibility: intermediate
              dtype: int
              description: Global maximum intensity.
              default: 65535
        levels:
              visibility: intermediate
              dtype: int
              description: Number of levels.
              default: 5

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
