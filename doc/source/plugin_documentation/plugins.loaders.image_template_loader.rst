Image Template Loader
#################################################################

Description
--------------------------

A class to load data from a folder of FabIO compatible images using data
descriptions loaded from a yaml file.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        yaml_file:
              visibility: basic
              dtype: filepath
              description: Path to the file containing the data descriptions.
              default: None
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
