Create a test for your plugin
*****************************

Testing something else in line with text example_

In order to submit a new plugin to Savu on Github, you **MUST** provide a test for your new plugin. 
To create a test follow the steps below:

    1. Choose a `test template`_
    2. Choose a `test dataset`_
    3. `Amend the parameters`_ r1,...,r8 in the file.
    4. Save the file.
    5. Add the file to your local repository.

.. _`test template`:

Test templates
==============
If your plugin is not dependent on any others (i.e. it can be run on its own on raw or corrected data), then download the 
:download:`sample test WITHOUT a process list<../files_and_images/example_test.py>`.  This will test the plugin with default parameters.

If your plugin is dependent on other plugins, you will need to create a process list **create a process list link** and download
the :download:`sample test WITH a process list <../files_and_images/example_test_with_process_list.py>`.


.. _`test dataset`:

Test data
=========

List of test data available. 
What to do if you require different test data. 
You can submit a new test dataset to Savu, with the requirement that it is less than 10MB in size.


.. _`Amend the parameters`:

Amending the parameters
=======================

See the real test modules:
    1. :download:`median_filter_test.py <../files_and_images/median_filter_test.py>` tests the median_filter_plugin.py plugin **WITH NO PROCESS LIST**.
    2. :download:`median_filter_test.py <../files_and_images/median_filter_test.py>` tests the median_filter_plugin.py plugin **WITH NO PROCESS LIST**.


Save the file as "your_module_name.py" 

.. warning:: Ensure the test file name has the same name as the module name (r1)

.. note:: Have a look at the :download:`real test <../files_and_images/median_filter_test.py>` for the median_filter_plugin.py module. 

List of test data available.
What to do if you require different test data. 

Internal crossreferences, like example_.

.. _example:

This is an example crossreference target. 
