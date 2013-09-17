Version 1.0.8 (dev)
-------------------

* Use ``long()`` for ID's, not ``int()``.


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
