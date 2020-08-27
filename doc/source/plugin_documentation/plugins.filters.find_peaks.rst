Find Peaks
#################################################################

Description
--------------------------

This plugin uses peakutils to find peaks in spectra. This is then metadata.

    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        out_datasets:
              visibility: datasets
              dtype: list
              description: 'Create a list of the dataset(s).'
              default: ['Peaks']
        thresh:
              visibility: basic
              dtype: float
              description: Threshold for peak detection
              default: 0.03
        min_distance:
              visibility: basic
              dtype: int
              description: Minimum distance for peak detection.
              default: 15

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
