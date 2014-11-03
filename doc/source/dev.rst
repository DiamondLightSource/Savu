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
which are detailed in the comments associated with the code.

Testing the new plugin
======================

So now that you have the new plugin written, you can test it using the following
command, you will need to make sure that savu is installed or included in your
$PYTHON_PATH

.. code:: bash

   python $SAVU_HOME/savu/test/framework_test.py -p $SAVU_HOME/plugin_examples/example_median_filter /tmp/savu_output/