Mrc Loader
########################################################

Description
--------------------------

Load Medical Research Council (MRC) formatted image data. 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        angles:
            visibility: basic
            dtype: "[str, int, None]"
            description: A python statement to be evaluated (e.g np.linspace(0, 180, nAngles)) or a file.
            default: None
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset
            default: tomo
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
