I13 Ptycho Loader
########################################################

Description
--------------------------

A class to load tomography data from an NXstxm file 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        mono_energy:
            visibility: basic
            dtype: float
            description: The mono energy.
            default: "9.1"
        
        is_tomo:
            visibility: intermediate
            dtype: bool
            description: Is tomo
            default: "True"
        
        theta_step:
            visibility: intermediate
            dtype: float
            description: The theta step.
            default: "1.0"
        
        theta_start:
            visibility: intermediate
            dtype: float
            description: The theta start.
            default: "-90.0"
        
        theta_end:
            visibility: intermediate
            dtype: float
            description: The theta end.
            default: "90.0"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
