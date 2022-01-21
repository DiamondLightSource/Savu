{% extends "plugin_template.rst" %}

{% block title %}Time Based Plus Drift Correction{% endblock %}

{% block description %}
Apply a time-based dark and flat field correction on data with an image drift using linear interpolation and template matching. 
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
        
        in_range:
            visibility: intermediate
            dtype: bool
            description: "Set corrected values to be in the range [0, 1]."
            default: "False"
        
        template:
            visibility: basic
            description: Region on the detector used to track the drift
            dtype: "list[str]"
            default: "['100:200', '100:200']"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.time_based_plus_drift_correction.rst{% endblock %}
