:orphan:

.. ::process_list:: test_data/process_lists/vo_centering_process.nxs
.. ::process_list:: test_data/process_lists/vo_centering_test.nxs

Projection Shift Documentation
#################################################################

    >>> add NxtomoLoader
    >>> mod 1.1 []
    >>> disp -a

(Change this) Include your plugin documentation here. Use a restructured text format.

..
    This is a comment. Include an image or file by using the following text
    ".. figure:: ../files_and_images/plugin_guides/plugins/alignment/projection_shift.png"


now you should be able to run up your python interpreter, and call

    >>> add ProjectionShift
    >>> disp 1.3 -vv
    >>> open test_data/process_lists/vo_centering_process.nxs



