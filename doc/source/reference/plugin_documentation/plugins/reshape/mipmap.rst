{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Mipmap{% endblock %}

{% block description %}
A plugin to downsample multidimensional data successively by powers of 2. The output is multiple 'mipmapped' datasets, each a power of 2 smaller in each dimension than the previous dataset. 
{% endblock %}

{% block parameter_yaml %}

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: hidden
            dtype: "[list[],list[str]]"
            description: Hidden out_datasets list as this is created dynamically.
            default: "[]"
        
        mode:
            visibility: basic
            dtype: str
            description: One of mean, median, min, max.
            default: mean
            options: "['mean', 'median', 'min', 'max']"
        
        n_mipmaps:
            visibility: basic
            dtype: int
            description: The number of successive downsamples of powers of 2 (e.g. n_mipmaps=3 implies downsamples (of the original data) of binsize 1, 2 and 4 in each dimension).
            default: "3"
        
        out_dataset_prefix:
            visibility: intermediate
            dtype: str
            description: The name of the dataset, to which the binsize will be appended for each instance.
            default: Mipmap
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.reshape.mipmap.rst{% endblock %}
