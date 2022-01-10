{% extends "plugin_template.rst" %}

{% block title %}Data Threshold{% endblock %}

{% block description %}
The module to threshold the data (less, lessequal, equal, greater, greaterequal) than the given value, based on the condition the data values will be replaced by the provided new value 
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
        
        inequality_condition:
            visibility: basic
            dtype: str
            description: Set to less, lessequal, equal, greater, greaterequal
            options: "['less', 'lessequal', 'equal', 'greater', 'greaterequal']"
            default: greater
        
        given_value:
            visibility: basic
            dtype: int
            description: The value to be replaced with by inequality_condition.
            default: "1"
        
        new_value:
            visibility: basic
            dtype: int
            description: The new value.
            default: "1"
        
        pattern:
            visibility: advanced
            dtype: str
            options: "['SINOGRAM', 'PROJECTION', 'VOLUME_XZ', 'VOLUME_YZ']"
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.basic_operations.data_threshold.rst{% endblock %}
