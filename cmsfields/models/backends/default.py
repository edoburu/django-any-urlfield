from django.db import models


class FileBrowseField(models.FileField):
    """
    The standard Django `~django.forms.FileField` with a `~django.forms.ClearableFileInput` widget.
    """
    pass


class ImageBrowseField(models.ImageField):
    """
    The standard Django `~django.forms.ImageField` with a `~django.forms.ClearableFileInput` widget.
    """
    pass
