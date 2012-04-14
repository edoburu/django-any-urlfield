Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-cmsfields

Or the current folder can be installed::

    pip install .

Configuration
-------------

Add the module to the installed apps::

    INSTALLED_APPS += (
        'cmsfields',
    )

Usage
-----

In a Django model, the field can be included:

.. code-block:: python

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from cmsfields.models.fields import CmsUrlField

    class MyModel(models.Model):
        title = models.CharField(_("title"), max_length=200)
        url = CmsUrlField(_("URL"))

By default, the ``CmsUrlField`` only supports linking to external pages.
To add support for your own models (e.g. an ``Article`` model),
include the following code in ``models.py``:

.. code-block:: python

    from cmsfields.models import CmsUrlField
    CmsUrlField.register_model(Article)

Now, the ``CmsUrlField`` offers users a dropdown field to directly select an article.

For more configuration options of the :func:`~cmsfields.models.CmsUrlField.register_model` function,
see the documentation of the :class:`~cmsfields.models.CmsUrlField` class.

