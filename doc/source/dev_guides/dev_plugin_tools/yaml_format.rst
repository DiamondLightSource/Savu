.. _yaml_format:

YAML format
###################

.. code-block:: yaml

    # What does YAML mean?​
    YAML:​
        -Y: YAML​
        -A: Ain't​
        -M: Markup​
        -L: Language

.. note::

    Markup Language is language which annotates text using tags or keywords in order to define how content is displayed



* YAML documents are a collection of key-value pairs​
* Indentation is used to denote structure
* The length of the indentation should not matter, as long as you are consistent inside the same file


Format examples
===================

.. code-block:: yaml

    # A list of numbers using hyphens:​
    numbers:​
        - one​
        - two​
        - three​
    ​
    # The inline version:​
    numbers: [ one, two, three ]


* Indent with spaces, not tabs​.
* There must be spaces between elements​


.. code-block::

    # This is correct​
    key: value​

    # This will fail​
    key:value


.. code-block:: yaml

    # Strings don't require quotes:​
    title: Introduction to YAML​
    ​
    # But you can still use them:​
    title-with-quotes: 'Introduction to YAML'​
    ​


* By prefixing a multi-line string with | you can preserve new lines​.
* By prefixing a multi-line string with > each line is interpreted as a space.
* Indenting each new line of a multi-line string will also mean that each new line is interpreted as a space.


.. code-block::

    # Write a multi-line string you don't want to appear as multi-line​
    # Each line interpreted as a space ​
    single-line-string: > ​
        This​
        should​
        be​
        one​
        line​

.. code-block::

    # Write a multi-line string you don't want to appear as multi-line​
    # Each line interpreted as a space ​
    single-line-string: This is also a multi line ​
        string. Each yaml line should be indented and then
        each new line will be interpreted as a space.


.. code-block::

    # Multiline strings start with |​
    multiple-lines: |​
        This string will maintain ​
        New lines​



References
=============

* https://dev.to/paulasantamaria/introduction-to-yaml-125f
* More information on yaml: https://yaml.org/spec/1.2/spec.html#Introduction