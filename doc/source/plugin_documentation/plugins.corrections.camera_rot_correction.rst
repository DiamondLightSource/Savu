Camera Rot Correction
#################################################################

Description
--------------------------

A plugin to apply a rotation to projection images, for example to correctfor missing camera alignment.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        angle:
              visibility: intermediate
              dtype: float
              description: The rotation angle for the output image in degrees.
              default: 0.0
        crop_edges:
              visibility: intermediate
              dtype: int
              description: When a rotation is applied to any image,
                the result will contain zeros around the edges, which can be removed by
                cropping the edges by a specified number of pixels.
              default: 0
        auto_crop:
              visibility: intermediate
              dtype: bool
              description: If activated, this feature will automatically
                crop the image to eliminate any regions without data
                (because of the rotation).
              default: False
        use_auto_centre:
              visibility: intermediate
              dtype: bool
              description: This parameter automatically sets the centre
                of rotation to the centre of the image. If set to False, the values
                from centre_x and centre_y are used. Note - The centre needs
                to be within the image dimensions.
              default: True
        center_x:
              visibility: intermediate
              dtype: float
              description: If not use_auto_centre, this value determines the
                detector x coordinate for the centre of rotation.
              default: 1279.5
        centre_y:
              visibility: intermediate
              dtype: float
              description: If not use_auto_centre, this value determines the
                detector x coordinate for the centre of rotation.
              default: 1079.5

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
