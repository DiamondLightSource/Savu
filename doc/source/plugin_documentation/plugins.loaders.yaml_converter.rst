Yaml Converter
#################################################################

Description
--------------------------

A class to load data from a non-standard nexus/hdf5 file using
descriptions loaded from a yaml file.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        yaml_file:
              visibility: basic
              dtype: filepath
              description: Path to the file containing the data descriptions.
              default: None
        template_param:
              visibility: hidden
              dtype: str
              description: A hidden parameter to hold parameters passed in
                via a savu template file.
              default: {}
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
