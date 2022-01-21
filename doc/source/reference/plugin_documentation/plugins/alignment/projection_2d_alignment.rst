{% extends "plugin_template.rst" %}

{% block title %}Projection 2D Alignment{% endblock %}

{% block description %}
A plugin to calculate horizontal-vertical shift vectors for fixing misaligned projection data by comparing with the re-projected data 
{% endblock %}

{% block parameter_yaml %}

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Default input dataset names.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: Default out dataset names.
            default: "['shifts']"
        
        upsample_factor:
            visibility: advanced
            dtype: int
            description: The upsampling factor. Registration accuracy is inversely propotional to upsample_factor.
            default: "10"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.alignment.projection_2d_alignment.rst{% endblock %}
