
{% block title %}title{% endblock %}
####################################################

Description
---------------

{% block description %}
{% endblock %}

.. dropdown:: Parameters

    .. code-block:: yaml

        {% block parameter_yaml %}
        {% endblock %}

    **Key**

    .. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
        :language: yaml

.. dropdown:: Citations

    {% block plugin_citations %}
    {% endblock %}


.. dropdown:: API

    .. include:: {% block plugin_file %}
                 {% endblock %}

