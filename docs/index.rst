
Welcome to django-any-urlfield's documentation!
===============================================

The ``any_urlfield`` module provides an improved URL selector
that supports both URLs to internal models and external URLs.

This addresses is a common challenge in CMS interfaces;
where providing a :class:`~django.forms.URLField` makes it hard to enter internal URLs,
while providing a :class:`~django.forms.ModelChoiceField` makes it too inflexible.

.. figure:: /images/anyurlfield1.*
   :width: 363px
   :height: 74px
   :alt: AnyUrlField, with external URL input.

.. figure:: /images/anyurlfield2.*
   :width: 290px
   :height: 76px
   :alt: AnyUrlField, with internal page input.


Relevant public classes:

* Model fields:

 * :class:`~any_urlfield.models.AnyUrlField`: allow users to choose either a model or external link as URL value

* Form widget rendering:

 * :class:`~any_urlfield.forms.HorizontalRadioFieldRenderer`
 * :class:`~any_urlfield.forms.SimpleRawIdWidget`

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

