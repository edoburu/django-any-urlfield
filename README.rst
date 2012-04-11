Introduction
============

The ``cmsfields`` module offers additional form widgets, useful to build CMS interfaces.

The main feature is the ``CmsUrlField``, which allows URLs to be entered
by either selecting an internal model, or entering an external URL.
This addresses is a common challenge in CMS interfaces;
where providing a ``URLField`` makes it hard to enter internal URLs,
while providing a ``ModelChoiceField`` makes it too inflexible.

Relevant public classes:

* Model fields:

 * ``CmsUrlField``: allow users to choose either a model or external link as URL value

* Form widget rendering:

 * ``HorizonatalRadioFieldRenderer``
 * ``SimpleRawIdWidget``


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

In a Django model, the field can be included::

    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    from cmsfields.models.fields import CmsUrlField

    class MyModel(models.Model):
        title = models.CharField(_("title"), max_length=200)
        url = CmsUrlField(_("URL"))

By default, the ``CmsUrlField`` only supports linking to external pages.
To add support for your own models (e.g. an ``Article`` model),
include the following code in ``models.py``::

    from cmsfields.models import CmsUrlField
    CmsUrlField.register_model(Article)

Now, the ``CmsUrlField`` offers users a dropdown field to directly select an article.
By default, it uses a ``django.forms.models.ModelChoiceField`` field with a ``django.forms.widgets.Select`` widget
to render the field.  This can be customized using the ``form_field`` and ``widget`` parameters::

    from cmsfields.models import CmsUrlField
    from cmsfields.forms.widgets import SimpleRawIdWidget

    CmsUrlField.register_model(Article, widget=SimpleRawIdWidget(Article))

Now, the ``Article`` model will be displayed as raw input field with a browse button.

