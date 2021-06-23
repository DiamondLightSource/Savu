I14 Fluo Loader
########################################################

Description
--------------------------

A class to load i14s xrf data 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        mono_path:
            visibility: basic
            dtype: h5path
            description: The mono energy.
            default: /entry/instrument/beamline/DCM/dcm_energy
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
