from __future__ import unicode_literals

import json

from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.test import TestCase

from any_urlfield.models import AnyUrlValue
from any_urlfield.tests import RegPageModel, UrlModel


class SerializerTests(TestCase):

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
