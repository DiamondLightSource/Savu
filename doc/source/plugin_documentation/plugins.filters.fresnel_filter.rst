Fresnel Filter
#################################################################

Description
--------------------------

Method similar to the Paganin filter working both on sinograms and
projections. Used to improve the contrast of the reconstruction image.

    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        ratio:
              visibility: datasets
              dtype: float
              description: Control the strength of the filter. Greater is stronger
              default: 100.0
        pattern:
              visibility: basic
              dtype: str
              description: Data processing pattern
              options: [PROJECTION, SINOGRAM]
              default: SINOGRAM

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
