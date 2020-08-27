Tiff Saver
#################################################################

Description
--------------------------

A class to save tomography data to tiff files
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data
            default: 'VOLUME_XZ'
        prefix:
            visibility: basic
            dtype: str
            description: Override the default output tiff file prefix.
            default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
