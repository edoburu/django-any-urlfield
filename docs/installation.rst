Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-any-urlfield

Or the current folder can be installed::

    pip install .

Configuration
-------------

Add the module to the installed apps::

    INSTALLED_APPS += (
        'any_urlfield',
    )

Usage
-----

In a Django model, the field can be included:

.. code-block:: python

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from any_urlfield.models import AnyUrlField

    class MyModel(models.Model):
        title = models.CharField(_("title"), max_length=200)
        url = AnyUrlField(_("URL"))

By default, the ``AnyUrlField`` only supports linking to external pages.
To add support for your own models (e.g. an ``Article`` model),
include the following code in ``models.py``:

.. code-block:: python

    from any_urlfield.models import AnyUrlField
    AnyUrlField.register_model(Article)

Now, the :class:`~any_urlfield.models.AnyUrlField` offers users a dropdown field to directly select an article.

For more configuration options of the :func:`~any_urlfield.models.AnyUrlField.register_model` function,
see the documentation of the :class:`~any_urlfield.models.AnyUrlField` class.

