Sinogram Alignment
#################################################################

Description
--------------------------

The centre of mass of each row is determined and then a sine function fit
through these to determine the centre of rotation.  The residual between
each centre of mass and the sine function is then used to align each row.
    
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
        
        threshold:
            visibility: basic
            dtype: str
            description: e.g. a.b will set all values above a to b.
            default: None
        
        p0:
            visibility: basic
            dtype: tuple
            description: Initial guess for the parameters of scipy.optimize.curve_fit.
            default: (1, 1, 1)
        
        type:
            visibility: intermediate
            dtype: list
            description: Either centre_of_mass or shift, with the latter requiring ProjectionVerticalAlignment prior to this plugin.
            default: centre_of_mass
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/documentation/short_parameter_key.yaml
    :language: yaml

Documentation
--------------------------

Citations
^^^^^^^^^^^^^^^^^^^^^^^^

Chemical imaging of single catalyst particles with scanning μ-XANES-CT and μ-XRF-CT by  Price, SWT et al.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The Tomographic filtering performed in this processing chain is derived from this work.

Bibtex
````````````````````````````````````````````````

.. code-block:: none

    @article{price2015chemical,
    title={Chemical imaging of single catalyst particles with scanning $\mu$-XANES-CT and $\mu$-XRF-CT},
    author={Price, SWT and Ignatyev, K and Geraki, K and Basham, M and Filik, J and Vo, NT and Witte, PT and Beale, AM and Mosselmans, JFW},
    journal={Physical Chemistry Chemical Physics},
    volume={17},
    number={1},
    pages={521--529},
    year={2015},
    publisher={Royal Society of Chemistry}}
    

Endnote
````````````````````````````````````````````````

.. code-block:: none

    %0 Journal Article
    %T Chemical imaging of single catalyst particles with scanning μ-XANES-CT and μ-XRF-CT
    %A Price, SWT
    %A Ignatyev, K
    %A Geraki, K
    %A Basham, M
    %A Filik, J
    %A Vo, NT
    %A Witte, PT
    %A Beale, AM
    %A Mosselmans, JFW
    %J Physical Chemistry Chemical Physics
    %V 17
    %N 1
    %P 521-529
    %D 2015
    %I Royal Society of Chemistry
    

