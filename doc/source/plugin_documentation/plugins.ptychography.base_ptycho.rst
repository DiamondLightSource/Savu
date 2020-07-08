Base Ptycho
#################################################################

Description
--------------------------

A base plugin for doing ptychography. Other ptychography plugins should
inherit from this.
    
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
              default: "['probe', 'object_transmission', 'positions']"

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
