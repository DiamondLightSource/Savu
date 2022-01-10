{% extends "plugin_template.rst" %}

{% block title %}Dark Flat Field Correction{% endblock %}

{% block description %}
A Plugin to apply a simple dark and flat field correction to data. 
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
        
        pattern:
            visibility: basic
            dtype: str
            options: "['SINOGRAM', 'PROJECTION']"
            description: Data processing pattern
            default: PROJECTION
        
        lower_bound:
            visibility: intermediate
            dtype: "[None,float]"
            description: Set all values below the lower_bound to this value.
            default: None
        
        upper_bound:
            visibility: intermediate
            dtype: "[None,float]"
            description: Set all values above the upper bound to this value.
            default: None
        
        warn_proportion:
            visibility: intermediate
            dtype: float
            description: Output a warning if this proportion of values, or greater, are below and/or above the lower/upper bounds. E.g. Enter 0.05 for 5%.
            default: "0.05"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.dark_flat_field_correction.rst{% endblock %}
