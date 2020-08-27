Pyfai Azimuthal Integrator With Bragg Filter
#################################################################

Description
--------------------------

Uses pyfai to remap the data. We then remap, percentile file and integrate.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        use_mask:
              visibility: basic
              dtype: bool
              description: Should we mask.
              default: False

        num_bins:
              visibility: basic
              dtype: int
              description: Number of bins.
              default: 1005

        num_bins_azim:
              visibility: intermediate
              dtype: int
              description: Number of azimuthal bins.
              default: 200
        thresh:
              visibility: intermediate
              dtype: list
              description: Threshold of the percentile filter
              default: '[5,95]'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
