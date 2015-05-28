Savu Developer Guide
********************

Developing new Plugins
======================

The architecture of the savu package is that new plugins can be easily developed
without having to take the framework into consideration.  This is mostly true for
simple cases, however there are some thigns which cannot be done with such 
simple methodologies and the developer may need to take more into consideration.

Every plugin in Savu needs to be a subclass of the Plugin class, however there 
are several convenience subclasses which already exist for doing standard 
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


Testing a new plugin using DAWN
===============================

DAWN can be downloaded from http://www.dawnsci.org/ and general user tutorials 
are found at https://www.youtube.com/user/DAWNScience

Using the Debug perspective, create a new test, e.g. "plugin_test_recon.py"
to test your plugin in "/Savu/savu/test/", in this case the 
"example_filter_back_projection.py" plugin for reconstructing data, setting the
self.plugin_name appropriately.  After saving the file, right-click on it in 
the PyDev Package Explorer window and Run As a Python unit-test

.. literalinclude:: ../../savu/test/plugin_test_recon.py
   :linenos:

This runs a series of tests and produces an output file with the result of the
plugin, whether it be a filter or a reconstruction, allowing for visualisation
of the data, providing a check of whether the process has worked successfully.

The output file is saved in a tmp directory as a .h5 file, e.g.
"/tmp/tmp32bexK.h5".  This can be viewed in DAWN.


Adding C/C++ extensions to a plugin
===================================

There are numerous ways to create python bindings to external C/C++ libraries, which may be useful to recycle existing code or to improve performance.  Two different approaches have currently been tested: Cython (to link to external C code) and Boost.Python (to link to external C++ code).  Cython is essentially python with C-types and requires a C-API, a python wrapper and a makefile, whilst Boost.Python is a wrapper for the Python/C API and requires a wrapper and a makefile. By building the makefile a shared library (*.so) file is created and can be added to the \lib directory in the Savu framework and imported as a python module.  

Cython example
--------------
http://docs.cython.org/src/tutorial/clibraries.html

1) A C interface: A *.pxd file, which is similar to a C header file, providing C function definitions required in the python code.

e.g. cdezing.pxd

.. literalinclude:: ../../extension_examples/cdezing.pyd

2) A python wrapper: A *.pyx file that must have a different name to the *.pyd file above. 

e.g. dezing.pyx

.. literalinclude:: ../../extension_examples/dezing.pyx

3) Makefile: In python this is a setup.py file.

e.g. setup.py

.. literalinclude:: ../../extension_examples/setup.py

Compile this file, passing appropriate C compiler flags if necessary, to obtain a *.so file.

::
	e.g.
	export CFLAGS="-I . $CFLAGS" \
	export LDFLAGS="-L . $LDFLAGS" \
	python setup.py build_ext -i

The output file for this example is a dezing.so file.  Transfer this file to \lib and import as a python module, e.g. import dezing

Boost.Python Example
--------------------
http://www.boost.org/doc/libs/1_58_0/libs/python/doc/

Boost.python aims to expose C++ classes/functions to python, without changing the original code. 

1) A python wrapper: Create the python module and define the external function names.

e.g. example_wrapper.cpp

.. literalinclude:: ../../extension_examples/example_wrapper.cpp

2) A makefile: A standard C++ makefile, incorporating Boost.Python path, to build a shared object library (*.so)

e.g. example_makefile

.. literalinclude:: ../../extension_examples/example_makefile

The output file for this example is a example.so file.  Transfer this file to \lib and import as a python module, e.g. import example, then simply access a function from within your python code as example.example_function1(...)

The example.hpp and example.cpp (below) along with example_wrapper.cpp, illustrate how to incorporate numpy arrays into the extension. 

.. literalinclude:: ../../extension_examples/example.hpp

.. literalinclude:: ../../extension_examples/example.cpp

