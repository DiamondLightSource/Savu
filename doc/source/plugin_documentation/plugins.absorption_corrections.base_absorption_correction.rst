Base Absorption Correction
#################################################################

Description
--------------------------

A base absorption correction for stxm and xrd
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        azimuthal_offset:
              visibility: basic
              dtype: float
              description: Angle between detectors.
              default: -90.0
        density:
              visibility: intermediate
              dtype: float
              description: The density
              default: 3.5377
        compound:
              visibility: intermediate
              dtype: str
              description: The compound
              default: 'Co0.1Re0.01Ti0.05(SiO2)0.84'
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

.. toctree::
    Plugin documention and guidelines on use </../documentation/base_absorption_correction_doc.rst>

