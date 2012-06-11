from django.db import models
from cmsfields.models.backends.default import FileBrowseField

__all__ = ('FileBrowseField', 'ImageBrowseField')


class ImageBrowseField(models.ImageField):
    """
    The standard Django `~django.forms.widgets.ImageField` with a preview.
    """
    def formfield(self, **kwargs):
        from cmsfields.forms.fields import ImagePreviewField
        from cmsfields.forms.widgets import ImagePreviewWidget
        kwargs['widget'] = ImagePreviewWidget   # hard override for admin
        defaults = {'form_class': ImagePreviewField}
        defaults.update(kwargs)
        return super(ImageBrowseField, self).formfield(**defaults)
