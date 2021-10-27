from django.core.exceptions import ValidationError
from django.test import TestCase

from any_urlfield.validators import ExtendedURLValidator


class ValidationTests(TestCase):
    maxDiff = None

    def test_url_validation(self):
        v = ExtendedURLValidator()
        v('https://google.com')
        v('tel://+44(0)123-45.67#8*9')
        v('mailto://test@example.com?subject=Greetings')

        self.assertRaises(ValidationError, v, 'tel://not a phone number')
        self.assertRaises(ValidationError, v, 'mailto://not an email address')
