{% extends "plugin_template.rst" %}

{% block title %}Image Saver{% endblock %}

{% block description %}
A class to save tomography data to image files.  Run the MaxAndMin plugin before this to rescale the data. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/savers/image_saver_doc.rst>

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
            visibility: hidden
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        pattern:
            visibility: basic
            dtype: str
            description: How to slice the data.
            default: VOLUME_XZ
        
        format:
            visibility: basic
            dtype: str
            description: Image format.
            default: tif
        
        num_bit:
            visibility: basic
            dtype: int
            description: Bit depth of the tiff format (8, 16 or 32).
            default: "16"
            options: "[8, 16, 32]"
        
        max:
            visibility: intermediate
            dtype: "[None,float]"
            description: Global max for tiff scaling.
            default: None
        
        min:
            visibility: intermediate
            dtype: "[None,float]"
            description: Global min for tiff scaling.
            default: None
        
        jpeg_quality:
            visibility: intermediate
            dtype: int
            description: JPEG encoding quality (1 is worst, 100 is best).
            default: "75"
        
        prefix:
            visibility: intermediate
            dtype: "[None,str]"
            description: Override the default output jpg file prefix
            default: None
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.savers.image_saver.rst{% endblock %}
