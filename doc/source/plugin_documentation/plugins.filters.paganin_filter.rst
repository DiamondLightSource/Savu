Paganin Filter
#################################################################

Description
--------------------------

A plugin to apply Paganin filter (contrast enhancement) on projections.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        Energy:
              visibility: basic
              dtype: float
              description: Given X-ray energy in keV.
              default: 53.0
        Distance:
              visibility: basic
              dtype: float
              description: 'Distance from sample to detection - Unit is
                metre.'
              default: 1.0
        Resolution:
              visibility: intermediate
              dtype: float
              description: 'Pixel size - Unit is micron.'
              default: 1.28
        Ratio:
              visibility: intermediate
              dtype: float
              description: 'Ratio of delta/beta.'
              default: 250.0
        Padtopbottom:
              visibility: intermediate
              dtype: float
              description: Pad to the top and bottom of projection.
              default: 10
        Padleftright:
              visibility: intermediate
              dtype: float
              description: Pad to the left and right of projection.
              default: 10
        Padmethod:
              visibility: intermediate
              dtype: str
              description: Numpy pad method.
              default: edge
        increment:
              visibility: intermediate
              dtype: float
              description: Increment all values by this amount before taking the
                log.
              default: 0.0

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
