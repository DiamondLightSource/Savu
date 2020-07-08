I08 Fluo Loader
#################################################################

Description
--------------------------

A class to load i08s xrf data
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        mono_path:
            visibility: basic
            dtype: int_path
            description: The mono energy.
            default: '/entry/instrument/PlaneGratingMonochromator/pgm_energy'

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
