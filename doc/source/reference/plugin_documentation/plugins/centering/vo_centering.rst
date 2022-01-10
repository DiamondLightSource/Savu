{% extends "plugin_template.rst" %}

{% block title %}Vo Centering{% endblock %}

{% block description %}
A plugin to calculate the centre of rotation using the Vo method 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/centering/vo_centering_doc.rst>

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
            description: The default names
            default: "['cor_preview', 'cor_broadcast']"
        
        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames (sinograms) to use in the calculation of the centre of rotation (this will not reduce the data size for subsequent plugins).
            default: "[]"
            example: "The typical three dimensional data structure is [angles, detY, detZ], e.g. for sinogram choose [:,sliceNo,:] [angles, detZ, detY]. If the data is four dimensional, include a time parameter."
        
        start_pixel:
            visibility: intermediate
            dtype: "[int,None]"
            description: The estimated centre of rotation. If value is None, use the horizontal centre of the image.
            default: None
        
        search_area:
            visibility: basic
            dtype: "list[float,float]"
            description: Search area around the estimated centre of rotation
            default: "[-50, 50]"
        
        ratio:
            visibility: intermediate
            dtype: float
            description: The ratio between the size of a sample and the field of view of a camera
            default: "0.5"
        
        search_radius:
            visibility: intermediate
            dtype: int
            description: Use for fine searching
            default: "6"
        
        step:
            visibility: intermediate
            dtype: float
            description: Step of fine searching
            default: "0.5"
        
        datasets_to_populate:
            visibility: intermediate
            dtype: "[list[],list[str]]"
            description: A list of datasets which require this information
            default: "[]"
        
        broadcast_method:
            visibility: advanced
            dtype: str
            options: "['median', 'mean', 'nearest', 'linear_fit']"
            description: 
                summary: Method of broadcasting centre values calculated from preview slices to full dataset.
                options: 
                    median: None
                    mean: None
                    nearest: None
                    linear_fit: None
            default: median
        
        row_drop:
            visibility: advanced
            dtype: int
            description: Drop lines around vertical center of the mask
            default: "20"
        
        average_radius:
            visibility: advanced
            dtype: int
            description: Averaging sinograms around a required sinogram to improve signal-to-noise ratio
            default: "5"
        
{% endblock %}

{% block plugin_citations %}
        
        **Reliable method for calculating the center of rotation in parallel-beam tomography by Vo, Nghia T et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{vo2014reliable,
            title={Reliable method for calculating the center of rotation in parallel-beam tomography},
            author={Vo, Nghia T and Drakopoulos, Michael and Atwood, Robert C and Reinhard, Christina},
            journal={Optics express},
            volume={22},
            number={16},
            pages={19078--19086},
            year={2014},
            publisher={Optical Society of America}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Reliable method for calculating the center of rotation in parallel-beam tomography
            %A Vo, Nghia T
            %A Drakopoulos, Michael
            %A Atwood, Robert C
            %A Reinhard, Christina
            %J Optics express
            %V 22
            %N 16
            %P 19078-19086
            %@ 1094-4087
            %D 2014
            %I Optical Society of America
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.centering.vo_centering.rst{% endblock %}
