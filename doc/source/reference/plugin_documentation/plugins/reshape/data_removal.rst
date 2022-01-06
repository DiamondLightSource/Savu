{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Data Removal{% endblock %}

{% block description %}
A class to remove any unwanted data from the specified pattern frame. 
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
        
        indices:
            visibility: basic
            dtype: "[list, str, None]"
            description: "A list or range of values to remove, e.g. [0, 1, 2] , 0:2 (start:stop) or 0:2:1 (start:stop:step)."
            default: None
        
        pattern:
            visibility: basic
            dtype: str
            description: Explicitly state the slicing pattern.
            default: SINOGRAM
        
        dim:
            visibility: basic
            dtype: int
            description: Data dimension to reduce.
            default: "0"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.reshape.data_removal.rst{% endblock %}
