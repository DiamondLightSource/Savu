Image Template Loader
#################################################################

Description
--------------------------

A class to load data from a folder of FabIO compatible images using data
descriptions loaded from a yaml file.
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to process
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s) to create
            default: []
        
        preview:
            visibility: basic
            dtype: int_list
            description: A slice list of required frames.
            default: []
        
        data_file:
            visibility: hidden
            dtype: str
            description: hidden parameter for savu template
            default: <>
        
        yaml_file:
            visibility: basic
            dtype: filepath
            description: Path to the file containing the data descriptions.
            default: None
        
        template_param:
            visibility: hidden
            dtype: str
            description: A hidden parameter to hold parameters passed in via a savu template file.
            default: 
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
