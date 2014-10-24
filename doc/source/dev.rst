Savu Developer Guide
********************

Developing new Plugins
======================

The archetecture of the savu package is that new plugins can be easily developed
without having to take the framework into consideration.  This is mostly true for
simple cases, however there are some thigns which cannot be done with such 
simple methodologies and the developer may need to take more into consideration.

Every plugin in Savu needs to be a subclass of the Plugin class, however there 
are several conviniece subclasses which already exist for doing standard 
processes such as filtering, reconstruction and augmentation/passthrough

Although there are many plugins defined in the core savu code, plugins can be 
written anywhere and included easily as shown below without having to be submitted
to the core code.

Median Filter Example
---------------------

This examples recreates one of the core plugins, a median filter.  The code is 
available in the main Savu repository under the plugin_examples folder.

.. literalinclude:: ../../plugin_examples/example_median_filter.py
   :linenos:

As you can see this is a pretty small implementation, and the key features of
it are as follows

**Line 31**
   This is where the class is desined, and we inherit from 2 classes, the 
   first is the Filter class, which deals with splitting the job up for us, and 
   provides some simple methods which we need to overload.  The second is the 
   CpuPlugin class which tells the framework that the processing that you are doing
   here runs on 1 cpu.

**line 41**
   All plugins have the populate_default_patamters method, in this you 
   need to add to the self.parameters dictionaly any parameters which you wish
   the end user to ultimatly be able to change, in this case we will let them
   define the size of the kernel we will use for out 3D median filter.  We initialise
   this with a good default value, in this case a tuple of (3, 3, 3)

**line 45**
   This is the first of the Filter class methods we need to implement.
   This basicaly says to the system how wide (how many frames) we want to see per
   filter step, a width of 0 means just the frame of interest, width 1 means 1 
   frame either side as well, etc.  In this case we need to ask for as many frames
   are required by the kernel size in the step direction.

**line 50**
   The second method we need to implement from the Filter class and the 
   part of the code that actually does all the work.  the input here 'data' will 
   contain the 3D block of data to process, and we need to return the data for the
   single frame in the middle of this.  In this case we use the scipy median filter
   with the 'kernmel_size' parameter, and return the middle slice.