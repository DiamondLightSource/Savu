{% extends "plugin_template.rst" %}

{% block title %}Ccpi Ring Artefact Filter{% endblock %}

{% block description %}
Regularization-based method for removing ring artifacts. 
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
        
        param_r:
            visibility: basic
            dtype: float
            description: The correction strength - decrease (typically in order of magnitude steps) to increase ring supression, or increase to reduce ring supression.
            default: "0.005"
        
        num_series:
            visibility: basic
            dtype: int
            description: High aspect ration compensation (for plate-like objects only)
            default: "1"
        
        param_n:
            visibility: intermediate
            dtype: int
            description: Unknown description (for plate-like objects only).
            default: "0"
        
{% endblock %}

{% block plugin_citations %}
        
        **Regularization methods for inverse problems in x-ray tomography by Titarenko, Valeriy et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @inproceedings{
            titarenko2010regularization,
            title={Regularization methods for inverse problems in x-ray tomography},
            author={Titarenko, Valeriy and Bradley, Robert and Martin, Christopher and Withers, Philip J and Titarenko, Sofya},
            booktitle={Developments in X-Ray Tomography VII},
            volume={7804},
            pages={78040Z},
            year={2010},
            organization={International Society for Optics and Photonics}
            }
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Conference Proceedings
            %T Regularization methods for inverse problems in x-ray tomography
            %A Titarenko, Valeriy
            %A Bradley, Robert
            %A Martin, Christopher
            %A Withers, Philip J
            %A Titarenko, Sofya
            %B Developments in X-Ray Tomography VII
            %V 7804
            %P 78040Z
            %D 2010
            %I International Society for Optics and Photonics
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.ring_removal.ccpi_ring_artefact_filter.rst{% endblock %}
