Statistics API
**************

The statistics class calculates and stores statistics information about the data as it goes through each plugin. Each plugin object contains a statistics object called **stats_obj**, through which stats are calculated and accessed. However the dictionaries that contain the statistics for each plugin are class attributes – they are shared across all the statistics object.

Calculating slice statistics
============================

Statistics are calculated frame by frame, in tandem with the processing of each frame/slice by a plugin. The method that does this is **set_slice_stats**, and is called for every frame. There is a dictionary within each stats object called **stats** that contains a list for each stat (max, min, mean etc). Every time **set_slice_stats** is called, these lists are appended with the stats for the last slice. The actual calculation of the statistics takes place in **calc_slice_stats**.

.. automethod:: savu.data.stats.statistics.Statistics.set_slice_stats

.. automethod:: savu.data.stats.statistics.Statistics.calc_slice_stats

Calculating volume statistics
=============================

At the end of the plugin, the method **set_volume_stats** is called, which deals all the post-processing tasks that need to be carried out. This method  combines slice stats to create volume stats. For example, the mean of all the slice-wide means is calculated to create a volume mean. These volume stats are then inserted into the dictionary **global_stats**, which is the class-wide dictionary that stores all the stats for all the plugins. The keys in **global_stats** are plugin numbers, with the values being a list containing the stats for that plugin. Usually this list has just one item, but for iterative plugins the list will have as many items as there were iterations of the plugin.

.. automethod:: savu.data.stats.statistics.Statistics.set_volume_stats

.. automethod:: savu.data.stats.statistics.Statistics.calc_volume_stats

Accessing stats
===============

Stats can be accessed within a plugin using the following methods:

.. automethod:: savu.data.stats.statistics.Statistics.get_stats

.. automethod:: savu.data.stats.statistics.Statistics.get_stats_from_name

.. automethod:: savu.data.stats.statistics.Statistics.get_stats_from_dataset

Which stats are calculated
==========================

The combination of stats that are calculated for a plugin depend on its stats object’s **stats_key**. This is a list containing the names of all the stats to be calculated. By default, it is set to max, min, mean, mean_std_dev, median_std_dev, NRMSD and zeros. This can be modified using the **set_stats_key** method, which should be called in the setup method of a plugin (if at all). It’s important to use this method rather than changing the stats_key directly, as this method checks all the stats it’s given are valid, and also updates an attribute called **slice_stats_key**, which is a list of all the slice-wide stats that are to be calculated.

.. automethod:: savu.data.stats.statistics.Statistics.set_stats_key

Writing stats to file and datasets
==================================

Stats are written to a hdf5 file, and also to the output datasets of each plugin with the following methods.

.. automethod:: savu.data.stats.statistics.Statistics._write_stats_to_file

.. automethod:: savu.data.stats.statistics.Statistics._link_stats_to_datasets

MPI
===

When Savu is being run with MPI, the slice-wide stats are split between each process (as the slices are). To correctly calculate volume-wide stats, these stats must all be collected together. This is done by the following method.

.. automethod:: savu.data.stats.statistics.Statistics._combine_mpi_stats

API
===

.. autoclass:: savu.data.stats.statistics.Statistics
   :undoc-members:

