Simple Fit Xrf
#################################################################

Description
--------------------------

This plugin fits XRF peaks.
    
Parameter definitions
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: list
            description: Create a list of the dataset(s)
            default: []
        
        out_datasets:
            visibility: datasets
            dtype: list
            description: A
            default: ['FitWeights', 'FitWidths', 'FitAreas', 'residuals']
        
        width_guess:
            visibility: intermediate
            dtype: float
            description: An initial guess at the width.
            default: 0.02
        
        mono_energy:
            visibility: intermediate
            dtype: float
            description: The mono energy
            default: 18.0
        
        peak_shape:
            visibility: intermediate
            dtype: str
            description: "What shape do you want?"
            default: gaussian
        
        pileup_cutoff_keV:
            visibility: intermediate
            dtype: float
            description: The cut off
            default: 5.5
        
        include_pileup:
            visibility: intermediate
            dtype: str
            description: Include pileup
            default: 1
        
        include_escape:
            visibility: intermediate
            dtype: int
            description: Include escape
            default: 1
        
        fitted_energy_range_keV:
            visibility: intermediate
            dtype: list
            description: The fitted energy range.
            default: [2.0, 18.0]
        
        elements:
            visibility: intermediate
            dtype: list
            description: The fitted elements,
            default: ['Zn', 'Cu', 'Ar']
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
