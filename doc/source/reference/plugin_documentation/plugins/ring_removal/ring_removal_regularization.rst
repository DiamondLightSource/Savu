Ring Removal Regularization
########################################################

Description
--------------------------

Regularization-based method working in the sinogram space to remove ring artifacts. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/ring_removal/ring_removal_regularization_doc.rst>

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
        
        alpha:
            visibility: basic
            dtype: float
            description: The correction strength. Smaller is stronger.
            default: "0.005"
        
        number_of_chunks:
            visibility: basic
            dtype: int
            description: Divide the sinogram to many chunks of rows.
            default: "1"
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

An analytical formula for ring artefact suppression in X-ray tomography by Titarenko, Sofya et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{titarenko2010analytical,
      title={An analytical formula for ring artefact suppression in X-ray tomography},
      author={Titarenko, Sofya and Withers, Philip J and Yagola, Anatoly},
      journal={Applied Mathematics Letters},
      volume={23},
      number={12},
      pages={1489--1495},
      year={2010},
      publisher={Elsevier}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T An analytical formula for ring artefact suppression in X-ray tomography
    %A Titarenko, Sofya
    %A Withers, Philip J
    %A Yagola, Anatoly
    %J Applied Mathematics Letters
    %V 23
    %N 12
    %P 1489-1495
    %@ 0893-9659
    %D 2010
    %I Elsevier
    

