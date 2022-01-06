{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Gmm Segment3D{% endblock %}

{% block description %}
A Plugin to segment data using Gaussian Mixtures from scikit 
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
        
        classes:
            visibility: basic
            dtype: int
            description: The number of classes for GMM
            default: "4"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.segmentation.gaussian_mixtures.gmm_segment3D.rst{% endblock %}
