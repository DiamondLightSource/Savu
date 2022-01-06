{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Quantisation Filter{% endblock %}

{% block description %}
A plugin to quantise an image into discrete levels. 
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
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        explicit_min_max:
            visibility: intermediate
            dtype: bool
            description: "False if min/max intensity comes from the metadata, True if it's user-defined."
            default: "False"
        
        min_intensity:
            visibility: intermediate
            dtype: int
            description: Global minimum intensity.
            default: "0"
        
        max_intensity:
            visibility: intermediate
            dtype: int
            description: Global maximum intensity.
            default: "65535"
        
        levels:
            visibility: intermediate
            dtype: int
            description: Number of levels.
            default: "5"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.filters.quantisation_filter.rst{% endblock %}
