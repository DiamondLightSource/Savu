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
            default: ['FitWeights', 'FitWidths', 'FitAreas', 'Backgrounds']
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the output dataset(s)
            default: ['Sum', 'Individual_curves']
        
        width_guess:
            visibility: intermediate
            dtype: float
            description: An initial guess at the width.
            default: 0.02
        
        peak_shape:
            visibility: intermediate
            dtype: str
            description: Which shape do you want.
            default: gaussian
        
        PeakIndex:
            visibility: intermediate
            dtype: list
            description: The peak index.
            default: []
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml
