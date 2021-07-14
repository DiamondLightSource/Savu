:orphan:

Developing a plugin with minimal effort
***************************************

Overview
========

The idea here is that with as little effort as possible it is possible to create
a plugin which can be used with Savu.  This is broken into a few simple steps:


Create a skeleton plugin
========================

First we need to create a new directory in your home area /home/yourusername/savu_plugins

The directory is automatially searched by Savu for plugins which you may have created, and 
the easiest way to get new plugins into the pipeline is to drop the plugin file into this directory

In this example we will use the ExampleMedianFilter, so copy this from ... to your new savu_plugins 
directory.  Use your favorite editor to change the 3 instances of ExampleMedianFilter to 
AddedMedianFilter and change the name of the file to added_median_fiter.py.


.. warning:: The Name of the plugin and its plugin file, must obey this common naming convention

Once you have saved the file you can move on to the next part of the process.


Creating a process list to test your plugin
===========================================

To test your plugin it needs to be included in a simple process list.  If you dont know how to set up a list, 
take a look at the user guides.  For a test list you want to include the minimum number of steps needed to 
observe that your plugin is providing the desired results.

If you have correctly done the above step, when you use the "list" command in the configurator, you should be able
to see your plugin in the resulting lists, and can then included it as you would any other plugin.

Once you have built a list, then save it to a convineint location for testing.

An example plugin list for testing the new plugin would be
  add NxtomoLoader
  add TimeseriesFieldCorrections
  add AddedMedianFilter
  add Hdf5TomoSaver
  save /tmp/AddedTest.nxs


Running the Process
===================

TBD
