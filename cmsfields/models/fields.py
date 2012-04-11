"""
Custom model fields to link to CMS content.
"""
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from cmsfields.models.values import CmsUrlValue
from cmsfields.registry import UrlTypeRegistry


class CmsUrlField(models.CharField):
    """
    A CharField that can either refer to a CMS page ID, or external URL.
    """
    __metaclass__ = models.SubfieldBase
    _static_registry = UrlTypeRegistry()

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('max_length'):
            kwargs['max_length'] = 300
        super(CmsUrlField, self).__init__(*args, **kwargs)


    @classmethod
    def register_model(cls, ModelClass, form_field, title=None, prefix=None):
        """
        Register a model to use in the URL field.
        """
        cls._static_registry.register(ModelClass, form_field, title, prefix)


    def formfield(self, **kwargs):
        # Associate formfield.
        # Import locally to avoid circular references.
        from cmsfields.forms.fields import CmsUrlFormField
        kwargs['form_class'] = CmsUrlFormField
        kwargs['url_type_registry'] = self._static_registry
        if kwargs.has_key('widget'):
            del kwargs['widget']
        return super(CmsUrlField, self).formfield(**kwargs)


    def to_python(self, value):
        if isinstance(value, CmsUrlValue):
            return value

        # Convert the string value
        if value is None:
            return None

        return CmsUrlValue.from_db_value(self._static_registry, value)

    def get_prep_value(self, value):
        # Convert back to string
        return value.to_db_value()


    def validate(self, value, model_instance):
        # Final validation of the field, before storing in the DB.
        super(CmsUrlField, self).validate(value, model_instance)
        if value:
            if value.type_prefix == 'http':
                validate_url = URLValidator()
                validate_url(value.type_value)
            elif value.type_value:
                if not value.exists():
                    raise ValidationError(self.error_messages['invalid_choice'] % value.type_value)


# Tell South how to create custom fields
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^cmsfields\.models\.fields\.CmsUrlField",
    ])
except ImportError:
    pass
