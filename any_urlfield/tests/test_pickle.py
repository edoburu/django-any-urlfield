from __future__ import unicode_literals

import pickle

from django.test import TestCase

from any_urlfield.models import AnyUrlValue
from any_urlfield.registry import UrlTypeRegistry
from any_urlfield.tests import PageModel

try:
    from StringIO import StringIO       # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3


class PickleTests(TestCase):

    def test_pickle_value(self):
        """
        See if regular fields can be pickled
        """
        v1 = AnyUrlValue.from_db_value("http://www.example.com/")
        out = StringIO()
        pickle.dump(v1, out)

        # Unpickle.
        out.seek(0)
        v2 = pickle.load(out)
        self.assertEqual(v1, v2)  # Note that __eq__ is overridden for AnyUrlValue

    def test_pickle_registry(self):
        """
        Test pickle when the ``AnyUrlValue`` has a custom registry.
        """
        reg = UrlTypeRegistry()
        urltype = reg.register(PageModel)
        page = PageModel.objects.create(slug='foo')

        # See if custom registries can be pickled
        v1 = AnyUrlValue(urltype.prefix, page.id, reg)
        out = StringIO()
        pickle.dump(v1, out)

        # Unpickle.
        out.seek(0)
        v2 = pickle.load(out)
        self.assertEqual(v1, v2)  # Note that __eq__ is overridden for AnyUrlValue!

        # See that the object still works properly
        self.assertEqual(v2.get_object(), page)
        self.assertEqual(str(v2), '/foo/')
