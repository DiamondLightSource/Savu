Ring Removal Fitting
########################################################

Description
--------------------------

Method to remove stripe artefacts in a sinogram (<-> ring artefacts in a reconstructed image) using a fitting-based method. It's suitable for use on low-contrast sinogram and/or for removing blurry rings. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/ring_removal/ring_removal_fitting_doc.rst>

Parameter definitions
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
        
        sigmax:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in x-direction which controls the strength of the removal.
            default: "5"
        
        sigmay:
            visibility: intermediate
            dtype: int
            description: Sigma of the Gaussian window in y-direction
            default: "20"
        
        order:
            visibility: intermediate
            dtype: int
            description: polynomial fit order.
            default: "2"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

Superior techniques for eliminating ring artifacts in X-ray micro-tomography by Vo, Nghia T et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{vo2018superior,
    title = {Superior techniques for eliminating ring artifacts in X-ray micro-tomography},
    author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
    journal={Optics express},
    volume={26},
    number={22},
    pages={28396--28412},
    year={2018},
    publisher={Optical Society of America}}
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T Superior techniques for eliminating ring artifacts in X-ray micro-tomography
    %A Vo, Nghia T
    %A Atwood, Robert C
    %A Drakopoulos, Michael
    %J Optics express
    %V 26
    %N 22
    %P 28396-28412
    %@ 1094-4087
    %D 2018
    %I Optical Society of America
    

