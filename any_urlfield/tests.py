from __future__ import unicode_literals
import json
import pickle

import django
from django import forms
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.serializers.base import DeserializationError
from django.db import models
from django.template import Template, Context
from django.test import TestCase
from any_urlfield.models import AnyUrlField, AnyUrlValue
from any_urlfield.registry import UrlTypeRegistry
from any_urlfield.validators import ExtendedURLValidator

try:
    from unittest import skipIf
except ImportError:
    from django.utils.unittest import skipIf  # Python 2.6

try:
    from django.utils import six
    unicode = six.text_type
except ImportError:
    pass  # Python 2, Django 1.3

try:
    from StringIO import StringIO       # Python 2
except ImportError:
    from io import BytesIO as StringIO  # Python 3


class UrlModel(models.Model):
    """
    Example model for testing AnyUrlField
    """
    url = AnyUrlField()

    def get_absolute_url(self):
        return str(self.url)


class PageModel(models.Model):
    """
    Example model to be linking to.
    """
    slug = models.SlugField()

    def get_absolute_url(self):
        return '/{0}/'.format(self.slug)


class RegPageModel(models.Model):
    slug = models.SlugField()

    def get_absolute_url(self):
        return '/{0}/'.format(self.slug)

AnyUrlField.register_model(RegPageModel)


class AnyUrlTests(TestCase):
    maxDiff = None

    def test_registry(self):
        """
        Test the basic registry setup.
        """
        reg = UrlTypeRegistry()
        self.assertIsNotNone(reg['http'])
        self.assertIsNotNone(reg['https'])

    def test_from_model(self):
        """
        Basic test of ``from_model``.
        """
        page2 = RegPageModel.objects.create(pk=1, slug='foo2')
        v = AnyUrlValue.from_model(page2)

        self.assertEqual(v.url_type.prefix, 'any_urlfield.regpagemodel')   # app_label.modelname
        self.assertEqual(v.type_value, page2.id)
        self.assertEqual(v.to_db_value(), 'any_urlfield.regpagemodel://1')

    def test_from_db_value(self):
        """
        Basic test of ``from_db_value``.
        """
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("http://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')
        self.assertEqual(v.type_value, "http://www.example.com/")
        self.assertEqual(unicode(v), "http://www.example.com/")

    def test_from_db_value_https(self):
        """
        Make sure other URLs are properly serialized.
        """
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("https://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')   # http is the constant for external URL types
        self.assertEqual(v.type_value, "https://www.example.com/")
        self.assertEqual(unicode(v), "https://www.example.com/")

    def test_from_db_value_ftps(self):
        """
        Make sure other URLs are properly serialized.
        """
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("ftps://www.example.com/", reg)
        self.assertEqual(v.type_prefix, 'http')   # http is the constant for external URL types
        self.assertEqual(v.type_value, "ftps://www.example.com/")
        self.assertEqual(unicode(v), "ftps://www.example.com/")

    def test_from_db_value_mailto(self):
        """
        Test constructing the value from ID.
        """
        reg = UrlTypeRegistry()

        v = AnyUrlValue.from_db_value("mailto://test@example.com", reg)
        self.assertEqual(v.type_prefix, 'http')   # http is the constant for external URL types
        self.assertEqual(v.type_value, "mailto://test@example.com")
        self.assertEqual(unicode(v), "mailto://test@example.com")

    def test_valid_db_id(self):
        """
        Make sure ID values are properly stored and serialized.
        """
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
        """
        Make sure invalid ID's are properly handled and recognized.
        """
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
        """
        Make sure empty value is treated as false.
        """
        x = AnyUrlValue.from_db_value('')
        self.assertFalse(1 if x else 0)
        self.assertFalse(x.exists())

    @skipIf(django.VERSION < (1, 8), "extended validation not supported in Django 1.7 and below")
    def test_url_validation(self):
        v = ExtendedURLValidator()
        v('https://google.com')
        v('tel://+44(0)123-45.67#8*9')
        v('mailto://test@example.com?subject=Greetings')

        self.assertRaises(ValidationError, v, 'tel://not a phone number')
        self.assertRaises(ValidationError, v, 'mailto://not an email address')

    def test_render_widget(self):
        """
        See if widget rendering is consistent between Django versions
        """
        from any_urlfield.forms import AnyUrlField

        reg = UrlTypeRegistry()
        reg.register(PageModel)

        class ExampleForm(forms.Form):
            field = AnyUrlField(url_type_registry=reg)

        def _normalize_html(html):
            # Avoid some differences in Django versions
            html = html.replace(' checked="checked"', '')
            html = html.replace(' checked', '')
            html = html.replace(' selected="selected"', ' selected')
            html = html.replace(' required', '')
            return html

        html = Template('{{ form.field }}').render(Context({'form': ExampleForm()}))
        self.assertHTMLEqual(_normalize_html(html), _normalize_html("""
<div class="related-widget-wrapper">
  <ul class="any_urlfield-url_type radiolist inline" id="id_field_0">
    <li>
      <label for="id_field_0_0">
        <input type="radio" name="field_0" value="http"
               class="any_urlfield-url_type radiolist inline" id="id_field_0_0"/>
        External URL</label>
    </li>
    <li>
      <label for="id_field_0_1">
        <input type="radio" name="field_0" value="any_urlfield.pagemodel"
               class="any_urlfield-url_type radiolist inline" id="id_field_0_1"/>
        page model</label>
    </li>
  </ul>

  <p class="any_urlfield-url-http" style="clear:left">
    <input type="text" name="field_1" class="vTextField" id="id_field_1"/>
  </p>

  <p class="any_urlfield-url-any_urlfieldpagemodel" style="clear:left">
    <select name="field_2" id="id_field_2">
      <option value="" selected>---------</option>
    </select>
  </p>
</div>
"""))

    def test_pickle(self):
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

    def test_db_empty_pre_save(self):
        """
        Make sure saving empty values works.
        """
        obj = UrlModel()
        obj.save()
        self.assertTrue(obj.pk)

    def test_db_pre_save(self):
        """
        Make sure saving works
        """
        obj = UrlModel(url=AnyUrlValue.from_db_value('http://www.example.org/'))
        obj.save()
        self.assertTrue(obj.pk)

    def test_dumpdata(self):
        """
        See if the dumpdata routines handle the value properly.
        """
        page2 = RegPageModel.objects.create(slug='foo2')
        UrlModel.objects.create(
            url=AnyUrlValue.from_model(page2)
        )

        json_data = serializers.serialize("json", UrlModel.objects.all())
        data = json.loads(json_data)
        self.assertEqual(data, [{"fields": {"url": "any_urlfield.regpagemodel://1"}, "model": "any_urlfield.urlmodel", "pk": 1}])

    def test_loaddata(self):
        """
        See if the loaddata routines handle the value properly.
        """
        fixture = '[{"fields": {"url": "any_urlfield.regpagemodel://999999"}, "model": "any_urlfield.urlmodel", "pk": 9}]'

        objects = serializers.deserialize('json', fixture)
        for deserializedobject in objects:
            deserializedobject.save()

        obj = UrlModel.objects.get(pk=9)
        value = obj.url
        self.assertEqual(value.type_prefix, 'any_urlfield.regpagemodel')
        self.assertEqual(value.type_value, 999999)

    def test_loaddata_exception(self):
        """
        Passing invalid values is simply not working.
        """
        fixture = '[{"fields": {"url": "unknown.unknown://999999"}, "model": "any_urlfield.urlmodel", "pk": 9}]'

        objects = serializers.deserialize('json', fixture)
        self.assertRaises(DeserializationError, lambda: list(objects))
