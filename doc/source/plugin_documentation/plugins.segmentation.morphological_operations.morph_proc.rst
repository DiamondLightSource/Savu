Morph Proc
#################################################################

Description
--------------------------

A Plugin to perform morphological operations on grayscale images
(use: erosion, dilation, opening, closing) or binary images
(use: binary_erosion, binary_dilation, binary_opening, binary_closing)
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        disk_radius:
            visibility: basic
            dtype: int
            description: The radius of the disk-shaped structuring element for morphology.
            default: 5

        morph_operation:
            visibility: intermediate
            dtype: int
            description: The type of morphological operation.
            default: 'binary_opening'
            options: [binary_erosion, binary_dilation, binary_opening, binary_closing]

        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: 'VOLUME_XZ'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
