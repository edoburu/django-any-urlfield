from __future__ import unicode_literals

from any_urlfield.forms import SimpleRawIdWidget
from any_urlfield.models import AnyUrlField
from django.db import models

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

AnyUrlField.register_model(RegPageModel, widget=SimpleRawIdWidget(RegPageModel))


# Import tests (Django 1.5-)
from .test_forms import FormTests
from .test_models import ModelTests
from .test_pickle import PickleTests
from .test_serializers import SerializerTests
from .test_validation import ValidationTests
