

Special features
----------------

.. _previewing:

Previewing
^^^^^^^^^^

Previewing enables the process list to be applied to a subset of the data.  Each loader plugin
has a preview parameter that is empty by default (apply processing to all the data).
The preview requires a list as input with entries for each data dimension.  Each entry in the preview
list should be of the form start:stop:step:chunk, where stop, step and chunk are optional
(defaults: stop = start + 1, step = 1, chunk = 1) but must be given in that order.  For more information
see :meth:`~savu.data.data_structures.preview.Preview.set_preview`


Previewing Examples
===================

The 3-D NxtomoLoader plugin maps the data dimensions (0, 1, 2) to the axis labels
(rotation_angle, detector_y, detector_x) respectively.


    >>> savu_config
    >>> add NxtomoLoader
    >>> mod 1.1 [:, mid-5:mid+6, :]     # process the middle 10 sinograms only
    >>> mod 1.1 [0:end:2, mid-5:mid+6, :]      # process every other projection
    >>> mod 1.1 [0:end:2, mid-5:mid+6, 300:end-300] # crop 300 pixels from the sides of the detector


.. _centering:

Sinogram centering
^^^^^^^^^^^^^^^^^^

Automatic calculation OR manual input of the centre of rotation are possible in Savu.


Auto-centering
==============

The auto-centering plugin (VoCentering) can be added to a process list before the reconstruction
plugin.  The value calculated in the centering routine is automatically passed to the reconstruction
and will override the centre_of_rotation parameter in the reconstruction plugin. The auto-centering
plugin is computationally expensive and should only be applied to previewed data.  There are two ways
to achieve this:

1. Apply previewing in the loader plugin to reduce the size of the processed data.

and/or

2. Apply previewing in VoCentering plugin (this will not reduce the size of the data).

.. note:: If you have applied previewing in the loader and again in the centering plugin you will be
          applying previewing to the previewed (reduced size) data.

See :ref:`autocentering`


Manual Centering
================

Ensure the VoCentering algorithm is not in the process list (remove it or turn it off if it is already
inside your list).  Modify the centre_of_rotation value in the reconstruction plugin, see
:ref:`manualcentering`.  If the manual centering value is approximate you can apply parameter
tuning, see :ref:`cor_parameter_tuning`


.. _parameter_tuning:

Parameter Tuning
^^^^^^^^^^^^^^^^^

If you wish to test a preview reconstruction with a range of values for a parameter, for instance,
if the centering is not quite optimal, then you can add different values separated by semi-colons.
Each ‘tuned’ parameter will add an extra dimension to the data.


Parameter tuning examples
=========================

    >>> mod 6.7 85;86;87        # three distinct values
    >>> mod 6.7 84:86:0.5;      # a range of values (start:stop:step) with semi-colon at the end
    >>> mod 6.6 FBP;CGLS        # values can be strings

See :ref:`eg2` and :ref:`cor_parameter_tuning`.

