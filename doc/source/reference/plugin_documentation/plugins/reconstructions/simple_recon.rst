{% extends "/home/glb23482/git_projects/Savu/doc/source/reference/savu_commands/plugin_template.rst" %}

{% block title %}Simple Recon{% endblock %}

{% block description %}
A Plugin to apply a simple reconstruction with no dependancies 
{% endblock %}

{% block plugin_citations %}
        
        **Principles of computerized tomographic imaging by Kak, Avinash C et al.**
        
        **Bibtex**
        
        .. code-block:: none
        
            @article{kak2002principles,
            title={Principles of computerized tomographic imaging},
            author={Kak, Avinash C and Slaney, Malcolm and Wang, Ge},
            journal={Medical Physics},
            volume={29},
            number={1},
            pages={107--107},
            year={2002},
            publisher={Wiley Online Library}}
            
        
        **Endnote**
        
        .. code-block:: none
        
            %0 Journal Article
            %T Principles of computerized tomographic imaging
            %A Kak, Avinash C
            %A Slaney, Malcolm
            %A Wang, Ge
            %J Medical Physics
            %V 29
            %N 1
            %P 107-107
            %@ 0094-2405
            %D 2002
            %I Wiley Online Library
            
        
        
{% endblock %}

{% block plugin_file %}../../../plugin_api/plugins.reconstructions.simple_recon.rst{% endblock %}
