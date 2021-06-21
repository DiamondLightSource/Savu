Image Template Loader
########################################################

Description
--------------------------

A class to load data from a folder of FabIO compatible images using data descriptions loaded from a yaml file. 

Parameter definitions
--------------------------

.. code-block:: yaml

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        yaml_file:
            visibility: basic
            dtype: "[None,yamlfilepath]"
            description: Path to the file containing the data descriptions.
            default: None
        
        template_param:
            visibility: hidden
            dtype: "[str,dict]"
            description: A hidden parameter to hold parameters passed in via a savu template file.
            default: 
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
