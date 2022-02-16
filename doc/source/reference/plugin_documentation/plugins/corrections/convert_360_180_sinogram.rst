{% extends "plugin_template.rst" %}

{% block title %}Convert 360 180 Sinogram{% endblock %}

{% block description %}
Method to convert a 360-degree sinogram to a 180-degree sinogram in a half-acquisition scan. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/corrections/convert_360_180_sinogram_doc.rst>

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
            description: Create a list of the output datatsets to create.
            default: "[]"
        
        center:
            visibility: basic
            dtype: float
            description: Center of rotation.
            default: "0.0"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.convert_360_180_sinogram.rst{% endblock %}
