{% extends "plugin_template.rst" %}

{% block title %}Nxtomo Loader{% endblock %}

{% block description %}
A class to load tomography data from a hdf5 file 
{% endblock %}

{% block parameter_yaml %}

        preview:
            visibility: basic
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        name:
            visibility: intermediate
            dtype: str
            description: A name assigned to the dataset.
            default: tomo
        
        data_path:
            visibility: basic
            dtype: str
            description: Path to the data inside the hdf/nxs file.
            default: entry1/tomo_entry/data/data
        
        image_key_path:
            visibility: intermediate
            dtype: "[None, h5path]"
            description: Path to the image key entry inside the nxs file. Set this parameter to None if use this loader for radiography.
            default: entry1/tomo_entry/instrument/detector/image_key
        
        dark:
            visibility: basic
            dtype: "[list[filepath, h5path, float],list[None,None,float]]"
            description: Specify the nexus file location where the dark field images are stored. Then specify the path within this nexus file, at which the dark images are located. The last value will be a scale value.
            default: "['None', 'None', 1.0]"
        
        flat:
            visibility: basic
            dtype: "[list[filepath, h5path, float],list[None,None,float]]"
            description: This parameter needs to be specified only if flats not stored in the same dataset as sample projections. Optional Path to the flat field data file, nxs path and scale value.
            default: "['None', 'None', 1.0]"
        
        angles:
            visibility: intermediate
            dtype: "[str, int, None]"
            description: If this is 4D data stored in 3D then pass an integer value equivalent to the number of projections per 180 degree scan. If the angles parameter is set to None, then values from default dataset used.
            default: None
        
        3d_to_4d:
            visibility: intermediate
            dtype: "[bool, int]"
            description: If this is 4D data stored in 3D then set this value to True, or to an integer value equivalent to the number of projections per 180-degree scan if the angles have not been set.
            default: "False"
        
        ignore_flats:
            visibility: intermediate
            dtype: "[list[int], None]"
            description: List of batch numbers of flats to ignore (starting at 1). Useful for excluding comprimised flats in combined data sets containing multiple batches of interspaced flats. The batch indexing begins at 1.
            default: None
        
{% endblock %}

{% block plugin_citations %}
    No citations
{% endblock %}

{% block plugin_file %}../../../../plugin_api/plugins.loaders.full_field_loaders.nxtomo_loader.rst{% endblock %}
