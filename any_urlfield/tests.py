from __future__ import unicode_literals
import pickle
from django.db import models
from django.test import TestCase
from any_urlfield.models import AnyUrlField, AnyUrlValue
from any_urlfield.registry import UrlTypeRegistry

try:
    from django.utils import six
    unicode = six.text_type
except ImportError:
    pass  # Python 2, Django 1.3

try:
    from StringIO import StringIO       # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3


class TestModel(models.Model):
    url = AnyUrlField()


class PageModel(models.Model):
    slug = models.SlugField()

    def get_absolute_url(self):
        return '/{0}/'.format(self.slug)


class AnyUrlTests(TestCase):

    def test_registry(self):
        reg = UrlTypeRegistry()
        self.assertIsNotNone(reg['http'])
        self.assertIsNotNone(reg['https'])


    def test_from_dbvalue(self):
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("http://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')
        self.assertEqual(v.type_value, "http://www.example.com/")
        self.assertEqual(unicode(v), "http://www.example.com/")


    def test_from_dbvalue_https(self):
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("https://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')   # http is the constant for external URL types
        self.assertEqual(v.type_value, "https://www.example.com/")
        self.assertEqual(unicode(v), "https://www.example.com/")


    def test_from_dbvalue_ftps(self):
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("ftps://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')   # http is the constant for external URL types
        self.assertEqual(v.type_value, "ftps://www.example.com/")
        self.assertEqual(unicode(v), "ftps://www.example.com/")


    def test_from_db_value_id(self):
        reg = UrlTypeRegistry()
        urltype = reg.register(PageModel)

        page = PageModel.objects.create(slug='foo')
        v = AnyUrlValue(urltype.prefix, page.id, reg)

        # Database state
        self.assertTrue(page.id)
        self.assertEqual(urltype.prefix, 'any_urlfield.pagemodel')   # app_label.modelname
        self.assertEqual(v.type_prefix, urltype.prefix)
        self.assertEqual(v.type_value, page.id)
        self.assertEqual(v.to_db_value(), 'any_urlfield.pagemodel://1')

        # Frontend
        self.assertEqual(unicode(v), "/foo/")          # fetches model and returns get_absolute_url()

        # Programmer API's
        self.assertIs(v.get_model(), PageModel)
        self.assertEqual(v.get_object(), page)
        self.assertTrue(v.exists())


    def test_invalid_db_id(self):
        reg = UrlTypeRegistry()
        urltype = reg.register(PageModel)
        v = AnyUrlValue(urltype.prefix, 999999, reg)

        # Database state
        self.assertEqual(v.type_value, 999999)
        self.assertEqual(v.to_db_value(), 'any_urlfield.pagemodel://999999')

        # Frontend
        from any_urlfield.models.values import logger
        logger.warning("NOTE: The following statement will cause a log to output")
        self.assertEqual(unicode(v), "#DoesNotExist")       # Avoids frontend errors

        # Programmer API's
        self.assertIs(v.get_model(), PageModel)
        self.assertRaises(PageModel.DoesNotExist, lambda: v.get_object())
        self.assertFalse(v.exists())


    def test_bool_empty(self):
        x = AnyUrlValue.from_db_value('')
        self.assertFalse(1 if x else 0)
        self.assertFalse(x.exists())


    def test_pickle(self):
        # See if regular fields can be pickled
        v1 = AnyUrlValue.from_db_value("http://www.example.com/")
        out = StringIO()
        pickle.dump(v1, out)

        # Unpickle.
        out.seek(0)
        v2 = pickle.load(out)
        self.assertEqual(v1, v2)  # Note that __eq__ is overridden for AnyUrlValue


    def test_pickle_registry(self):
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
