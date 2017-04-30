from __future__ import unicode_literals

import django
from any_urlfield.validators import ExtendedURLValidator
from django.core.exceptions import ValidationError
from django.test import TestCase

try:
    from unittest import skipIf
except ImportError:
    from django.utils.unittest import skipIf  # Python 2.6


class ValidationTests(TestCase):
    maxDiff = None

    @skipIf(django.VERSION < (1, 8), "extended validation not supported in Django 1.7 and below")
    def test_url_validation(self):
        v = ExtendedURLValidator()
        v('https://google.com')
        v('tel://+44(0)123-45.67#8*9')
        v('mailto://test@example.com?subject=Greetings')

        self.assertRaises(ValidationError, v, 'tel://not a phone number')
        self.assertRaises(ValidationError, v, 'mailto://not an email address')
