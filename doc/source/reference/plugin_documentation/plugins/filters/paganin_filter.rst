Paganin Filter
########################################################

Description
--------------------------

A plugin to apply the Paganin filter (for denoising or contrast enhancement) on projections. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/filters/paganin_filter_doc.rst>

Parameters
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        Ratio:
            visibility: basic
            dtype: float
            description: Ratio of delta/beta.
            default: "250.0"
        
        Energy:
            visibility: basic
            dtype: float
            description: Beam energy in keV.
            default: "53.0"
        
        Distance:
            visibility: basic
            dtype: float
            description: Distance from sample to detector. Unit is metre.
            default: "1.0"
        
        Resolution:
            visibility: basic
            dtype: float
            description: Pixel size. Unit is micron.
            default: "1.28"
        
        Padtopbottom:
            visibility: intermediate
            dtype: int
            description: Pad to the top and bottom of projection.
            default: "100"
        
        Padleftright:
            visibility: intermediate
            dtype: int
            description: Pad to the left and right of projection.
            default: "100"
        
        Padmethod:
            visibility: intermediate
            dtype: str
            description: Numpy pad method.
            default: edge
        
        increment:
            visibility: intermediate
            dtype: float
            description: Increment all values by this amount before taking the log.
            default: "0.0"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

Simultaneous phase and amplitude extraction from a single defocused image of a homogeneous object by Paganin, David et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{paganin2002simultaneous,
    title={Simultaneous phase and amplitude extraction from a single defocused image of a homogeneous object},
    author={Paganin, David and Mayo, Sheridan C and Gureyev, Tim E and Miller, Peter R and Wilkins, Steve W},
    journal={Journal of microscopy},
    volume={206},
    number={1},
    pages={33--40},
    year={2002},
    publisher={Wiley Online Library}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T Simultaneous phase and amplitude extraction from a single defocused image of a homogeneous object
    %A Paganin, David
    %A Mayo, Sheridan C
    %A Gureyev, Tim E
    %A Miller, Peter R
    %A Wilkins, Steve W
    %J Journal of microscopy
    %V 206
    %N 1
    %P 33-40
    %@ 0022-2720
    %D 2002
    %I Wiley Online Library
    

