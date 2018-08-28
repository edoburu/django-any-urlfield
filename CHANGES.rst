Changelog
=========

Verseion 2.6.1 (2018-08-28)
---------------------------

* Fixed infinite recursion on ``AnyUrlValue.get_object()`` on unpicked values.


Version 2.6 (2018-08-27)
------------------------

* Dropped Django 1.7 support
* Optimized formset display - avoid N-queries when ``AnyUrlField.resolve_objects()`` is used.


Version 2.5.1 (2018-08-23)
--------------------------

* Fixed ``AnyUrlField.resolve_objects()`` to handle nullable values.


Version 2.5 (2018-08-21)
------------------------

* Added Django 2.0 and 2.1 support
* Added ``AnyUrlField.resolve_objects()`` to perform bulk lookups for data in querysets and lists.
* Added ``AnyUrlValue.resolve_values()`` to perform bulk lookups for a list of value objects.
* Dropped Django 1.4, 1.5, 1.6 and 1.7 support


Version 2.4.2 (2017-07-31)
--------------------------

* Fixed form ``has_changed`` check, preventing inline fieldsets to be submitted.
* Fixed widget alignment inside inlines.


Version 2.4.1 (2017-05-05)
--------------------------

* Fixed packaging bugs that prevented including the HTML templates for Django 1.11.


Version 2.4 (2017-05-01)
------------------------

* Added Django 1.11 support.
* Dropped Python 2.6 support.
* Fix for empty value.


Version 2.3 (2017-02-03)
------------------------

* For Django 1.8 and up, the ``URLValidator`` now allows more
  URL schemes by default, specifically ``mailto:`` and ``tel:`` URLs.


Version 2.2.1 (2016-02-26)
--------------------------

* Fixed Django 1.10 deprecation warnings.


Version 2.2 (2015-12-30)
------------------------

* Added Django 1.9 support
* Fixed saving blank/null values.


Version 2.1.1 (2015-04-15)
--------------------------

* Fix Django 1.7/1.8 model saving issues.
* Added ``AnyUrlValue.from_model()`` to directly wrap a model into an ``AnyUrlValue``.


Version 2.1 (2015-04-10)
------------------------

* Added Django 1.8 support
* Fix importing json fixture data.

Released as 2.1a1: (2014-09-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added caching support for URL values.


Version 2.0.4 (2014-12-30)
--------------------------

* Fixed Python 3.3 issues


Version 2.0.3 (2014-10-30)
--------------------------

* Fixed ``__eq__()`` for comparing against other object types.


Version 2.0.2 (2014-10-30)
--------------------------

* Added pickle support.
* Fixed Django 1.7 support.


Version 2.0.1 (2014-09-15)
--------------------------

* Fix performance issue with form fields.


Version 2.0 (2014-08-15)
------------------------

Released as 2.0b1 (2014-06-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Improved Python 3 support.
* Delay initialisation of ``ModelChoiceField`` objects.
* Fix ``exists()`` value for empty URLs


Released as 2.0a1 (2014-04-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added Python 3 support
* Allow passing callables to the form_field parameter of ``AnyUrlField.register_model``


Version 1.0.12 (2014-02-24)
---------------------------

* Implement ``AnyUrlField.__deepcopy__()`` to workaround Django < 1.7 issue,
  where ``__deepcopy__()`` is missing for ``MultiValueField`` classes.


Version 1.0.11 (2014-02-20)
---------------------------

* Improve external URL support (https, ftps, smb, etc..)
* Fix unnecessary query at registration of custom models.


Version 1.0.10 (2013-12-12)
---------------------------

* Fix using ``AnyUrlField`` with ``blank=True``.
* Fix ``_has_changed`` is no longer used in django >= 1.6.0


Version 1.0.9 (2013-10-15)
--------------------------

* Fixed exporting the value in the ``dumpdata`` command.


Version 1.0.8 (2013-09-20)
--------------------------

* Use ``long()`` for ID's, not ``int()``.
* Improve ``ObjectDoesNotExist`` check in ``AnyUrlValue.__unicode__()``, to support model translations.


Version 1.0.7 (2013-05-28)
--------------------------

* Fix using this widget with Django 1.6 alpha 1


Version 1.0.5 (2013-05-07)
--------------------------

* Fix errors during south migration
* Fix errors when deleting rows in an inline formset which uses an ``AnyUrlField``.


Version 1.0.4 (2013-05-02)
--------------------------

* Fix https URL support


Version 1.0.3 (2013-04-24)
--------------------------

* Fix change detection, to support formsets and admin inlines.
* Fix widget alignment within a ``TabularInline``.


Version 1.0.2 (2013-01-24)
--------------------------

* Fix ``setup.py`` code to generate translation files for the ``sdist``.
* Remove ``HorizonatalRadioFieldRenderer`` from the public API.


Version 1.0.1 (2012-12-27)
--------------------------

* Use jQuery live events to support using the ``AnyUrlField`` in Django inlines.



Version 1.0.0 (2012-12-27)
--------------------------

First PyPI release.

The module design has been stable for quite some time,
so it's time to release this module to the public.
