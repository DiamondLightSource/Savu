
What is a Process list
------------------------

Savu is a framework that does nothing if you run it on its own.  It requires a process list, passed to it
at runtime along with the data, to detail the processing steps it should follow.  A Savu process list is
created using the Savu configurator tool, which stacks together :ref:`'plugins'<savu_plugin>` chosen from a
repository. Each plugin performs a specific independent task, such as correction, filtering, reconstruction.
For a list of available plugins see :ref:`plugin documentation list<plugin_doc_list>`.

.. or :ref:`plugin API <plugin_api_list>`