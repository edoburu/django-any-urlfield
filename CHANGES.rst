Version 1.0.11
--------------

* Improve external URL support (https, ftps, smb, etc..)
* Fix unnecessary query at registration of custom models.


Version 1.0.10
--------------

* Fix using ``AnyUrlField`` with ``blank=True``.
* Fix ``_has_changed`` is no longer used in django >= 1.6.0


Version 1.0.9
-------------

* Fixed exporting the value in the ``dumpdata`` command.


Version 1.0.8
-------------

* Use ``long()`` for ID's, not ``int()``.
* Improve ``ObjectDoesNotExist`` check in ``AnyUrlValue.__unicode__()``, to support model translations.


Version 1.0.7
-------------

* Fix using this widget with Django 1.6 alpha 1


Version 1.0.5
-------------

* Fix errors during south migration
* Fix errors when deleting rows in an inline formset which uses an ``AnyUrlField``.


Version 1.0.4
-------------

* Fix https URL support


Version 1.0.3
-------------

* Fix change detection, to support formsets and admin inlines.
* Fix widget alignment within a ``TabularInline``.


Version 1.0.2
-------------

* Fix ``setup.py`` code to generate translation files for the ``sdist``.
* Remove ``HorizonatalRadioFieldRenderer`` from the public API.


Version 1.0.1
-------------

* Use jQuery live events to support using the ``AnyUrlField`` in Django inlines.


Version 1.0.0
-------------

First PyPI release.

The module design has been stable for quite some time,
so it's time to release this module to the public.
