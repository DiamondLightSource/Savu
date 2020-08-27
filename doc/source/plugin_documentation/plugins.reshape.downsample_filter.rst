Downsample Filter
#################################################################

Description
--------------------------

A plugin to reduce the data in the selected dimension by a proportion.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        bin_size:
            visibility: basic
            dtype: list
            description: Bin Size for the downsample.
            default: 2
        mode:
            visibility: basic
            dtype: int
            description: One of 'mean', 'median', 'min', 'max'.
            default: 'mean'
        pattern:
            visibility: basic
            dtype: int
            description:  One of 'PROJECTION' or 'SINOGRAM'.
            default: PROJECTION

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
