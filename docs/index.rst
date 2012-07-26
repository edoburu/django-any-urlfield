
Welcome to django-cmsfields's documentation!
============================================

The ``cmsfields`` module offers additional form widgets, useful to build CMS interfaces.

The main feature is the ``CmsUrlField``, which allows URLs to be entered
by either selecting an internal model, or entering an external URL.
This addresses is a common challenge in CMS interfaces;
where providing a ``URLField`` makes it hard to enter internal URLs,
while providing a ``ModelChoiceField`` makes it too inflexible.

.. figure:: /images/cmsurlfield1.*
   :width: 363px
   :height: 74px
   :alt: CmsUrlField, with external URL input.

.. figure:: /images/cmsurlfield2.*
   :width: 290px
   :height: 76px
   :alt: CmsUrlField, with internal page input.


Relevant public classes:

* Model fields:

 * :class:`~cmsfields.models.CmsUrlField`: allow users to choose either a model or external link as URL value

* Form widget rendering:

 * :class:`~cmsfields.forms.HorizonatalRadioFieldRenderer`
 * :class:`~cmsfields.forms.SimpleRawIdWidget`
 * :class:`~cmsfields.forms.ImagePreviewWidget`

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

