from __future__ import unicode_literals

from any_urlfield.forms import SimpleRawIdWidget
from any_urlfield.models import AnyUrlField
from django.contrib import admin
from django.db import models


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
admin.site.register(RegPageModel)  # Needed for SimpleRawIdWidget to render


# Import tests (Django 1.5-)
from .test_forms import FormTests
from .test_models import ModelTests
from .test_pickle import PickleTests
from .test_serializers import SerializerTests
from .test_validation import ValidationTests
