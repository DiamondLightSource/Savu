{% extends "plugin_template.rst" %}

{% block title %}Distortion Correction{% endblock %}

{% block description %}
A plugin to apply radial distortion correction. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/corrections/distortion_correction_doc.rst>

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
        
        polynomial_coeffs:
            visibility: basic
            dtype: list
            description: Parameters of the radial distortion
            default: "[1.0, 0.0, 0.0, 0.0, 0.0]"
        
        center_from_top:
            visibility: basic
            dtype: float
            description: The centre of distortion in pixels from the top of the image.
            default: "1080.0"
        
        center_from_left:
            visibility: basic
            dtype: float
            description: The centre of distortion in pixels from the left of the image.
            default: "1280.0"
        
        file_path:
            visibility: basic
            dtype: "[None,filepath]"
            description: Path to the text file having distortion coefficients. Set to None for manually inputing.
            default: None
        
        crop_edges:
            visibility: basic
            dtype: int
            description: When applied to previewed/cropped data, the result may contain zeros around the edges, which can be removed by cropping the edges by a specified number of pixels
            default: "0"
        
{% endblock %}

{% block plugin_citations %}
        
        **Radial lens distortion correction with sub-pixel accuracy for X-ray micro-tomography by Vo, Nghia T et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{vo2015radial,
              title={Radial lens distortion correction with sub-pixel accuracy for X-ray micro-tomography},
              author={Vo, Nghia T and Atwood, Robert C and Drakopoulos, Michael},
              journal={Optics express},
              volume={23},
              number={25},
              pages={32859--32868},
              year={2015},
              publisher={Optical Society of America}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Radial lens distortion correction with sub-pixel accuracy for X-ray micro-tomography
            %A Vo, Nghia T
            %A Atwood, Robert C
            %A Drakopoulos, Michael
            %J Optics express
            %V 23
            %N 25
            %P 32859-32868
            %@ 1094-4087
            %D 2015
            %I Optical Society of America
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.corrections.distortion_correction.rst{% endblock %}
