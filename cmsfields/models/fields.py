"""
Custom model fields to link to CMS content.
"""
from cms.models.fields import PageField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from filebrowser.fields import FileBrowseField
from cmsfields.forms import URL_TYPE_EXTERNAL
from cmsfields.forms.fields import PageChoiceField
from cmsfields.models.values import CmsUrlValue


class SimplePageField(PageField):
    """
    A foreignkey to a page, with simple single Select box as default widget.
    """
    default_form_class = PageChoiceField


class CmsUrlField(models.CharField):
    """
    A CharField that can either refer to a CMS page ID, or external URL.
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 300
        super(CmsUrlField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # Associate formfield.
        # Import locally to avoid circular references.
        from cmsfields.forms.fields import CmsUrlFormField
        kwargs['form_class'] = CmsUrlFormField
        if kwargs.has_key('widget'):
            del kwargs['widget']
        return super(CmsUrlField, self).formfield(**kwargs)

    def to_python(self, value):
        if isinstance(value, CmsUrlValue):
            return value

        # Convert the string value
        if value is None:
            return None

        return CmsUrlValue.from_db_value(value)

    def get_prep_value(self, value):
        # Convert back to string
        return value.to_db_value()

    def validate(self, value, model_instance):
        # Final validation of the field, before storing in the DB.
        super(CmsUrlField, self).validate(value, model_instance)
        if value:
            if value.url_type_id == URL_TYPE_EXTERNAL:
                validate_url = URLValidator()
                validate_url(value.url)
            elif value.object_id:
                if not value.exists():
                    raise ValidationError(self.error_messages['invalid_choice'] % value.object_id)


class ImageBrowseField(FileBrowseField):
    """
    A filebrowse field with default configuration for images.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 300,
            'format': 'Image'
        }

        # Format the help text in a consistent manner.
        if kwargs.has_key('help_size'):
            defaults['help_text'] = u"De afbeelding wordt geschaald naar %s \u00d7 %s pixels." % tuple(kwargs['help_size'].split('x'))
            del kwargs['help_size']

        defaults.update(kwargs)
        super(ImageBrowseField, self).__init__(*args, **defaults)


# Tell South how to create custom fields
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^cmsfields\.models\.fields\.CmsUrlField",
        "^cmsfields\.models\.fields\.ImageBrowseField",
    ])
except ImportError:
    pass
