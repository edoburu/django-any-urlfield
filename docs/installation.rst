Installation
============

First install the module, preferably in a virtual environment::

    pip install django-any-urlfield

Add the module to the installed apps:

.. code-block:: python

    INSTALLED_APPS += (
        'any_urlfield',
    )

Usage
-----

Add the field to a Django model:

.. code-block:: python

    from django.db import models
    from any_urlfield.models import AnyUrlField

    class MyModel(models.Model):
        title = models.CharField("Title", max_length=200)
        url = AnyUrlField("URL")

By default, the ``AnyUrlField`` only supports linking to external pages.

Register any model that the ``AnyUrlField`` should support linking to:

.. code-block:: python

    from any_urlfield.models import AnyUrlField
    AnyUrlField.register_model(Article)

Now, the :class:`~any_urlfield.models.AnyUrlField` offers users a dropdown field to directly select an article.

The default field is a :class:`django.forms.models.ModelChoiceField` field
with a :class:`django.forms.widgets.Select` widget.
This can be customized using the ``form_field`` and ``widget`` parameters:

.. code-block:: python

    from any_urlfield.models import AnyUrlField
    from any_urlfield.forms import SimpleRawIdWidget

    AnyUrlField.register_model(Article, widget=SimpleRawIdWidget(Article))

That will display the ``Article`` model as raw input field with a browse button.

For more configuration options of the :func:`~any_urlfield.models.AnyUrlField.register_model` function,
see the documentation of the :class:`~any_urlfield.models.AnyUrlField` class.

