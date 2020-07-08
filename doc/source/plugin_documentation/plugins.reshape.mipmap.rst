Mipmap
#################################################################

Description
--------------------------

A plugin to downsample multidimensional data successively by powers of 2.
The output is multiple 'mipmapped' datasets, each a power of 2 smaller in
each dimension than the previous dataset.
    
Parameter definitions
--------------------------

.. code-block:: yaml

    
        mode:
            visibility: basic
            dtype: str
            description: "One of mean, median, min, max."
            default: 'mean'
            options: [mean, median, min, max]

        n_mipmaps:
            visibility: basic
            dtype: int
            description: "The number of successive downsamples of powers
              of 2 (e.g. n_mipmaps=3 implies downsamples (of the original
              data) of binsize 1, 2 and 4 in each dimension)."
            default: 3

        out_dataset_prefix:
            visibility: intermediate
            dtype: str
            description: The name of the dataset, to which the binsize
              will be appended for each instance.
            default: 'Mipmap'

        out_datasets:
            visibility: datasets
            dtype: list
            description: Hidden out_datasets list as this is created
              dynamically.
            default: []

        
Key
^^^^^^^^^^

.. literalinclude:: /../source/documentation/short_parameter_key.yaml
    :language: yaml
