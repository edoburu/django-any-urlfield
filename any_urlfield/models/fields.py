"""
Custom model fields to link to CMS content.
"""
from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six

from any_urlfield.models.values import AnyUrlValue
from any_urlfield.registry import UrlTypeRegistry
from any_urlfield.validators import ExtendedURLValidator


class AnyUrlField(models.CharField):
    """
    A CharField that can either refer to a CMS page ID, or external URL.

    .. figure:: /images/anyurlfield1.*
       :width: 363px
       :height: 74px
       :alt: AnyUrlField, with external URL input.

    .. figure:: /images/anyurlfield2.*
       :width: 290px
       :height: 76px
       :alt: AnyUrlField, with internal page input.

    By default, the ``AnyUrlField`` only supports linking to external pages.
    To add support for your own models (e.g. an ``Article`` model),
    include the following code in :file:`models.py`:

    .. code-block:: python

        from any_urlfield.models import AnyUrlField
        AnyUrlField.register_model(Article)

    Now, the ``AnyUrlField`` offers users a dropdown field to directly select an article.
    By default, it uses a :class:`django.forms.ModelChoiceField` field with a :class:`django.forms.Select` widget
    to render the field.  This can be customized using the ``form_field`` and ``widget`` parameters:

    .. code-block:: python

        from any_urlfield.models import AnyUrlField
        from any_urlfield.forms import SimpleRawIdWidget

        AnyUrlField.register_model(Article, widget=SimpleRawIdWidget(Article))

    Now, the ``Article`` model will be displayed as raw input field with a browse button.
    """
    _static_registry = UrlTypeRegistry()  # Also accessed by AnyUrlValue as internal field.

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 300
        super(AnyUrlField, self).__init__(*args, **kwargs)

    @classmethod
    def register_model(cls, ModelClass, form_field=None, widget=None, title=None, prefix=None):
        """
        Register a model to use in the URL field.

        This function needs to be called once for every model
        that should be selectable in the URL field.

        :param ModelClass: The model to register.
        :param form_field: The form field class used to render the field. This can be a lambda for lazy evaluation.
        :param widget: The widget class, can be used instead of the form field.
        :param title: The title of the model, by default it uses the models ``verbose_name``.
        :param prefix: A custom prefix for the model in the serialized database format. By default it uses "appname.modelname".
        """
        cls._static_registry.register(ModelClass, form_field, widget, title, prefix)

    def formfield(self, **kwargs):
        # Associate formfield.
        # Import locally to avoid circular references.
        from any_urlfield.forms.fields import AnyUrlField as AnyUrlFormField
        kwargs['form_class'] = AnyUrlFormField
        kwargs['url_type_registry'] = self._static_registry
        if 'widget' in kwargs:
            del kwargs['widget']
        return super(AnyUrlField, self).formfield(**kwargs)

    def from_db_value(self, value, expression, connection, context):
        # This method is used to cast DB values to python values.
        # The call to to_python() is not used anymore.
        if value is None:
            return None
        return AnyUrlValue.from_db_value(value, self._static_registry)

    def to_python(self, value):
        if isinstance(value, AnyUrlValue):
            return value

        # Convert the string value
        if value is None:
            return None

        return AnyUrlValue.from_db_value(value, self._static_registry)

    def get_prep_value(self, value):
        if isinstance(value, six.string_types):
            # Happens with south migration
            return value
        elif value is None:
            return None if self.null else ''
        else:
            # Convert back to string
            return value.to_db_value()

    def pre_save(self, model_instance, add):
        # Make sure that the SQL compiler in doesn't get an AnyUrlValue,
        # but a regular 'str' object it can write to the database.
        value = super(AnyUrlField, self).pre_save(model_instance, add)
        if not value:
            return None
        else:
            return value.to_db_value()

    def value_to_string(self, obj):
        # For dumpdata and serialization
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        # Final validation of the field, before storing in the DB.
        super(AnyUrlField, self).validate(value, model_instance)
        if value:
            if value.type_prefix == 'http':
                validate_url = ExtendedURLValidator()
                validate_url(value.type_value)
            elif value.type_value:
                if not value.exists():
                    raise ValidationError(self.error_messages['invalid_choice'] % value.type_value)

    @classmethod
    def resolve_objects(cls, objects, skip_cached_urls=False):
        """
        Make sure all AnyUrlValue objects from a set of objects is resolved in bulk.
        This avoids making a query per item.

        :param objects: A list or queryset of models.
        :param skip_cached_urls: Whether to avoid prefetching data that has it's URL cached.
        """
        # Allow the queryset or list to consist of multiple models.
        # This supports querysets from django-polymorphic too.
        queryset = list(objects)
        any_url_values = []

        for obj in queryset:
            model = obj.__class__
            for field in _any_url_fields_by_model[model]:
                any_url_value = getattr(obj, field)
                if any_url_value and any_url_value.url_type.has_id_value:
                    any_url_values.append(any_url_value)

        AnyUrlValue.resolve_values(any_url_values, skip_cached_urls=skip_cached_urls)


class _ModelFieldsCache(defaultdict):
    def __missing__(self, model):
        from .fields import AnyUrlField
        value = [
            f.name for f in model._meta.get_fields() if isinstance(f, AnyUrlField)
        ]
        self[model] = value
        return value


_any_url_fields_by_model = _ModelFieldsCache()
