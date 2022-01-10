{% extends "plugin_template.rst" %}

{% block title %}Camera Rot Correction{% endblock %}

{% block description %}
A plugin to apply a rotation to projection images, for example to correct for missing camera alignment. 
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
        
        angle:
            visibility: basic
            dtype: float
            description: The rotation angle for the output image in degrees.
            default: "0.0"
        
        crop_edges:
            visibility: intermediate
            dtype: int
            description: When a rotation is applied to any image, the result will contain unused values around the edges, which can be removed by cropping the edges by a specified number of pixels.
            default: "0"
        
        auto_crop:
            visibility: basic
            dtype: bool
            description: If activated, this feature will automatically crop the image to eliminate any regions without data (because of the rotation).
            default: "False"
        
        use_auto_centre:
            visibility: intermediate
            dtype: bool
            description: This parameter automatically sets the centre of rotation to the centre of the image. If set to False, the values from centre_x and centre_y are used. Note - The centre needs to be within the image dimensions.
            default: "True"
        
        center_x:
            visibility: intermediate
            dtype: float
            description: If not use_auto_centre, this value determines the detector x coordinate for the centre of rotation.
            default: "1279.5"
        
        centre_y:
            visibility: intermediate
            dtype: float
            description: If not use_auto_centre, this value determines the detector x coordinate for the centre of rotation.
            default: "1079.5"
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.camera_rot_correction.rst{% endblock %}
