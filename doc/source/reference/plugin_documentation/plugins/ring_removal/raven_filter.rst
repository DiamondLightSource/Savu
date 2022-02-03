{% extends "plugin_template.rst" %}

{% block title %}Raven Filter{% endblock %}

{% block description %}
FFT-based method for removing ring artifacts. 
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
        
        uvalue:
            visibility: basic
            dtype: int
            description: Cut-off frequency. To control the strength of filter, e.g. strong=10, moderate=20, weak=50.
            default: "20"
        
        vvalue:
            visibility: basic
            dtype: int
            description: Number of image-rows around the zero-frequency to be applied the filter.
            default: "1"
        
        nvalue:
            visibility: intermediate
            dtype: int
            description: To define the shape of filter
            default: "8"
        
        padFT:
            visibility: intermediate
            dtype: int
            description: Padding for Fourier transform.
            default: "50"
        
{% endblock %}

{% block plugin_citations %}
        
        **Numerical removal of ring artifacts in microtomography by Raven, Carsten et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{raven1998numerical,
            title={Numerical removal of ring artifacts in microtomography},
            author={Raven, Carsten},
            journal={Review of scientific instruments},
            volume={69},
            number={8},
            pages={2978--2980},
            year={1998},
            publisher={American Institute of Physics}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Numerical removal of ring artifacts in microtomography
            %A Raven, Carsten
            %J Review of scientific instruments
            %V 69
            %N 8
            %P 2978-2980
            %@ 0034-6748
            %D 1998
            %I American Institute of Physics
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.ring_removal.raven_filter.rst{% endblock %}
