Savu Standardisation Document
=============================

**Space:** Each dataset belongs to a data space.  The data space that a dataset belongs to can be
determined by it's axis labels and meta data.

A space consists of:
    - **axis_labels** : The name associated with each axis.
    - **meta_data**   : Meta data required alongside the dataset.
    - **patterns**    : How the data can be accessed (sliced).
    - **plugins**     : Available plugins.
    - **inheritance** : Spaces this space inherits from.
    - **mappings**    : Spaces that the plugins in this space can map to.


**Axis label:**  An axis label is the name associated with a data dimension.  Each loader plugin
provides a mapping of the axis labels to the data dimensions, so the order of the data dimensions
does not matter.

Available axis labels:
    - detector_x
    - detector_y
    - rotation_angle
    - scan
    - energy
    - voxel_x
    - voxel_y
    - voxel_z

NB:  A plugin should only ever request a data dimension by specifying its axis_label using the
function <map to function here>


**Meta data:**  This is any additional mandatory information required alongside the dataset. 

Available meta data:
    - angles
    - dark
    - flat


**Pattern:** Data access patterns describe how a dataset should be sliced. Each data space has
a set of patterns associated with it and each pattern associates each axis label data dimension
with a core or slice dimension.  If a plugin requests a particular pattern, it will receive all
of the core dimensions and *n* slice dimensions, where *n=1,...* is specified in the plugin.
The same pattern can be associated with data of differing dimensionality.

Available patterns:

    - SINOGRAM:
        - core_dims: rotation_angle, detector_x
        - required_slice_dims: detector_y
        - optional_slice_dims: scan, energy
    - PROJECTION:
        - core_dims: detector_x, detector_y
        - required_slice_dims: rotation_angle
        - optional_slice_dims: scan, energy
    - VOLUME: (VOLUME_XY, VOLUME_YZ, VOLUME_XZ)
        - core_dims: two of volume_x, volume_y, volume_z
        - required_slice_dims: one of volume_x, volume_y, volume_z
        - optional_slice_dims: scan, energy
    - TIMESERIES:
        - core_dims: detector_x, detector_y
        - required_slice_dims: scan, rotation_angle
        - optional_slice_dims: energy
    - DIFFRACTION:



Description of all spaces
-------------------------

tomo_raw:
    - inheritance:
    - axis_labels: detector_x, detector_y, rotation_angle
    - meta_data:   dark, flat, angles
    - patterns:    PROJECTION, SINOGRAM
    - plugins:     distortion_correction, dezing, correction?
    - mappings:    tomo_raw

tomo:
    - inheritance:
    - axis_labels:  detector_x, detector_y, rotation_angle
    - meta_data:    angles
    - patterns:     PROJECTION, SINOGRAM
    - plugins:
    - mappings:     volume

volume:
    - inheritance:
    - axis_labels:  volume_x, volume_y, volume_z (scan, energy)
    - meta_data: 
    - patterns:     VOLUME
    - plugins:      
    - mappings:

time_tomo_raw:
    - inheritance:  tomo_raw
    - axis_labels:  scan
    - meta_data:
    - patterns:     TIMESERIES
    - plugins=      plugins...
    - mappings:

time_tomo:
    - inheritance   tomo
    - axis_labels:  scan
    - meta_data:
    - patterns:     PROJECTION, SINOGRAM
    - plugins:      
    - mappings:


Required in the future?
-----------------------

energy_tomo_raw:
    - axis_labels=detector_x, detector_y, rotation_angle, energy
    - meta_data=angles, dark, flat
    - patterns=projection, sinogram
    - plugins=plugins...
    - inheritance=tomo_raw
    - mappings: volume

energy_time_tomo_raw:
    - axis_labels=detector_x, detector_y, rotation_angle, energy, scan
    - meta_data=angles, dark, flat
    - patterns=projection, sinogram
    - plugins=plugins...
    - inheritance=time_tomo_raw, energy_tomo_raw
    - mappings: volume

    

