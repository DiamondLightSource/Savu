{% extends "plugin_template.rst" %}

{% block title %}Morph Proc{% endblock %}

{% block description %}
A Plugin to perform morphological operations on grayscale images (use: erosion, dilation, opening, closing) or binary images (use: binary_erosion, binary_dilation, binary_opening, binary_closing) 
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
        
        disk_radius:
            visibility: basic
            dtype: int
            description: The radius of the disk-shaped structuring element for morphology.
            default: "5"
        
        morph_operation:
            visibility: intermediate
            dtype: int
            description: The type of morphological operation.
            default: binary_opening
            options: "['binary_erosion', 'binary_dilation', 'binary_opening', 'binary_closing']"
        
        pattern:
            visibility: intermediate
            dtype: str
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.segmentation.morphological_operations.morph_proc.rst{% endblock %}
