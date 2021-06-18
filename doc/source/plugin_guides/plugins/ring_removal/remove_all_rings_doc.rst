:orphan:

.. ::process_list:: test_data/test_process_lists/filters/ring_removal/remove_all_rings_test.nxs

Remove All Rings Documentation
#################################################################

(Change this) Include your plugin documentation here. Use a restructured text format.

.. figure:: ../../../files_and_images/plugin_guides/example.jpg
   :figwidth: 50 %
   :align: center
   :figclass: align-center

An example of adding RingRemoval to your plugin list:

    >>> add RemoveAllRings
    >>> mod 1.3 2.0
    >>> disp -vv

    >>> open test_data/test_process_lists/filters/ring_removal/remove_all_rings_test.nxs
    >>> disp -v