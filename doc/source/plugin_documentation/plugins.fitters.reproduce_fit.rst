Reproduce Fit
#################################################################

Description
--------------------------

This plugin reproduces the fitted curves. Its for diagnostics.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the input dataset(s)
            default: ["FitWeights", "FitWidths", "FitAreas","Backgrounds"]

        out_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the output dataset(s)
            default: ["Sum", "Individual_curves"]


        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
