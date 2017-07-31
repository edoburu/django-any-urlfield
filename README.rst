.. image:: https://img.shields.io/travis/edoburu/django-any-urlfield/master.svg?branch=master
    :target: http://travis-ci.org/edoburu/django-any-urlfield
.. image:: https://img.shields.io/pypi/v/django-any-urlfield.svg
    :target: https://pypi.python.org/pypi/django-any-urlfield/
.. image:: https://img.shields.io/pypi/l/django-any-urlfield.svg
    :target: https://pypi.python.org/pypi/django-any-urlfield/
.. image:: https://img.shields.io/codecov/c/github/edoburu/django-any-urlfield/master.svg
    :target: https://codecov.io/github/edoburu/django-any-urlfield?branch=master

django-any-urlfield
===================

The ``any_urlfield`` module provides an improved URL selector
that supports both URLs to internal models and external URLs.

This addresses is a common challenge in CMS interfaces;
where providing a ``URLField`` makes it hard to enter internal URLs,
while providing a ``ModelChoiceField`` makes it too inflexible.
This package provides the both of both worlds.

For more details, see the documentation_ at Read The Docs.


Screenshot
==========

.. figure:: https://github.com/edoburu/django-any-urlfield/raw/master/docs/images/anyurlfield1.png
   :width: 363px
   :height: 74px
   :alt: AnyUrlField, with external URL input.

.. figure:: https://github.com/edoburu/django-any-urlfield/raw/master/docs/images/anyurlfield2.png
   :width: 290px
   :height: 76px
   :alt: AnyUrlField, with internal page input.


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

Now, the ``AnyUrlField`` offers users a dropdown field to directly select an article.

The default field is a ``django.forms.models.ModelChoiceField`` field
with a ``django.forms.widgets.Select`` widget.
This can be customized using the ``form_field`` and ``widget`` parameters:

.. code-block:: python

    from any_urlfield.models import AnyUrlField
    from any_urlfield.forms import SimpleRawIdWidget

    AnyUrlField.register_model(Article, widget=SimpleRawIdWidget(Article))

That will display the ``Article`` model as raw input field with a browse button.


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)


.. _documentation: https://django-any-urlfield.readthedocs.io/

