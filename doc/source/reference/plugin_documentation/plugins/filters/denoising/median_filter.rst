{% extends "plugin_template.rst" %}

{% block title %}Median Filter{% endblock %}

{% block description %}
A plugin to apply 2D/3D median filter. The 3D capability is enabled through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size and in 3D case kernel_size x kernel_size x kernel_size. 

.. toctree::
    Plugin documention and guidelines on use </../../../plugin_guides/plugins/filters/denoising/median_filter_doc.rst>

{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.filters.denoising.median_filter.rst{% endblock %}
