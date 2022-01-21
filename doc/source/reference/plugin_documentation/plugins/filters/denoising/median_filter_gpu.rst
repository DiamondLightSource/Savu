{% extends "plugin_template.rst" %}

{% block title %}Median Filter Gpu{% endblock %}

{% block description %}
A plugin to apply 2D/3D median filter on a GPU. The 3D capability is enabled    through padding. Note that the kernel_size in 2D will be kernel_size x kernel_size and in 3D case kernel_size x kernel_size x kernel_size. 
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.filters.denoising.median_filter_gpu.rst{% endblock %}
