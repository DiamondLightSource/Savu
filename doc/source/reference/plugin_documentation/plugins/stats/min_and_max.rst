{% extends "plugin_template.rst" %}

{% block title %}Min And Max{% endblock %}

{% block description %}
A plugin to calculate the min and max values of each slice (as determined by the pattern parameter) 
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
            description: The default names.
            default: "['the_min', 'the_max']"
        
        method:
            visibility: basic
            dtype: str
            options: "['extrema', 'percentile']"
            description: Method to find the global min and the global max.
            default: percentile
        
        p_range:
            visibility: basic
            dtype: "list[float,float]"
            description: "Percentage range if use the 'percentile' method."
            default: "[0.0, 100.0]"
        
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data.
            default: VOLUME_XZ
        
        smoothing:
            visibility: intermediate
            dtype: bool
            description: Apply a smoothing filter or not.
            default: "True"
        
        masking:
            visibility: intermediate
            dtype: bool
            description: Apply a circular mask or not.
            default: "True"
        
        ratio:
            visibility: intermediate
            dtype: "[None,float]"
            description: Used to calculate the circular mask. If not provided, it is calculated using the center of rotation.
            default: None
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.stats.min_and_max.rst{% endblock %}
