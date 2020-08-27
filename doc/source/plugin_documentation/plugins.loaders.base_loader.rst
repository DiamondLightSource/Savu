Base Loader
#################################################################

Description
--------------------------

A base class for loader plugins. A base plugin from which all
data loader plugins should inherit.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        preview:
              visibility: basic
              dtype: int_list
              description: A slice list of required frames.
              default: []
        data_file:
              visibility: hidden
              dtype: str
              description: hidden parameter for savu template
              default: '<>'
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

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
