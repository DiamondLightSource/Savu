{% extends "plugin_template.rst" %}

{% block title %}Find Peaks{% endblock %}

{% block description %}
This plugin uses peakutils to find peaks in spectra and add them to the metadata. 
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
            default: "['Peaks']"
        
        thresh:
            visibility: basic
            dtype: float
            description: Threshold for peak detection
            default: "0.03"
        
        min_distance:
            visibility: basic
            dtype: int
            description: Minimum distance for peak detection.
            default: "15"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.filters.find_peaks.rst{% endblock %}
