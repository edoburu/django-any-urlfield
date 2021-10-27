from any_urlfield.forms import SimpleRawIdWidget
from any_urlfield.models import AnyUrlField
from django.contrib import admin
from django.db import models


class UrlModel(models.Model):
    """
    Example model for testing AnyUrlField
    """
    url = AnyUrlField()

    def __str__(self):
        return str(self.url)

    def get_absolute_url(self):
        return str(self.url)


class PageModel(models.Model):
    """
    Example model to be linking to.
    """
    slug = models.SlugField()

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return '/{}/'.format(self.slug)


class RegPageModel(models.Model):
    slug = models.SlugField()

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return '/{}/'.format(self.slug)


AnyUrlField.register_model(RegPageModel, widget=SimpleRawIdWidget(RegPageModel))
admin.site.register(RegPageModel)  # Needed for SimpleRawIdWidget to render
