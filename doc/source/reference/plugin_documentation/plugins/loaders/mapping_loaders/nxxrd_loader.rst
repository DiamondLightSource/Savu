{% extends "plugin_template.rst" %}

{% block title %}Nxxrd Loader{% endblock %}

{% block description %}
A class to load tomography data from an NXxrd file. 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        name:
            visibility: basic
            dtype: str
            description: The name assigned to the dataset.
            default: xrd
        
        calibration_path:
            visibility: basic
            dtype: "[None,str]"
            description: Path to the calibration file
            default: None
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.loaders.mapping_loaders.nxxrd_loader.rst{% endblock %}
