Distortion Correction Deprecated
#################################################################

Description
--------------------------

A plugin to apply radial distortion correction.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        polynomial_coeffs:
              visibility: intermediate
              dtype: tuple
              description: Parameters of the radial distortion
              default: (1.00015076, 1.9289e-6, -2.4325e-8, 1.00439e-11, -3.99352e-15)
        centre_from_top:
              visibility: intermediate
              dtype: float
              description: The centre of distortion in pixels from the top
                of the image.
              default: 995.24
        centre_from_left:
              visibility: intermediate
              dtype: float
              description: The centre of distortion in pixels from the left
                of the image.
              default: 1283.25
        crop_edges:
              visibility: intermediate
              dtype: int
              description: When applied to previewed/cropped data, the
                result may contain zeros around the edges, which can be
                removed by cropping the edges by a specified number of pixels
              default: 0

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
