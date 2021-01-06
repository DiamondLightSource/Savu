:orphan:

.. ::process_list:: test_data/process_lists/simple_tomo_pipeline_cpu.nxs

Remove All Rings Documentation
#################################################################

(Change this) Include your plugin documentation here. Use a restructured text format.

.. figure:: ../../../files_and_images/plugin_guides/example.jpg
   :figwidth: 50 %
   :align: center
   :figclass: align-center

An example of adding RingRemoval to your plugin list:

    >>> add RemoveAllRings
    >>> mod 1.3 FBP
    >>> disp -vv

    >>> open test_data/process_lists/simple_tomo_pipeline_cpu.nxs
    >>> disp -v