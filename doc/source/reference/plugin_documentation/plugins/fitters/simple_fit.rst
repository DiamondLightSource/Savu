Simple Fit
########################################################

Description
--------------------------

This plugin fits peaks. 

Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s)
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Create a list of the dataset(s)
            default: "['FitWeights', 'FitWidths', 'FitAreas', 'residuals']"
        
        width_guess:
            visibility: basic
            dtype: float
            description: An initial guess at the width.
            default: "0.02"
        
        peak_shape:
            visibility: intermediate
            dtype: str
            description: Which shape do you want.
            default: gaussian
        
        PeakIndex:
            visibility: basic
            dtype: "[list[],list]"
            description: The peak index
            default: "[]"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
