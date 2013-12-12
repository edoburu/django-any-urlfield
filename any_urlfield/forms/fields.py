"""
Custom form fields for URLs
"""
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from any_urlfield.forms.widgets import AnyUrlWidget
from any_urlfield.models.values import AnyUrlValue


class AnyUrlField(forms.MultiValueField):
    """
    Form field that combines a Page ID and external page URL.

    The form field is used automatically when
    the :class:`~any_urlfield.models.AnyUrlField` is used in the model.
    """
    widget = AnyUrlWidget


    def __init__(self, url_type_registry, max_length=None, *args, **kwargs):
        self.url_type_registry = url_type_registry  # UrlTypeRegistry object

        # Build fields,
        # these have to match the widget.
        fields = []
        choices = []
        for urltype in self.url_type_registry:
            # Get formfield, update properties
            field = urltype.form_field
            field.required = False   # Delay check, happens somewhere else.
            if getattr(field, 'max_length', None) and field.max_length > max_length:
                field.max_length = max_length

            fields.append(field)
            choices.append((urltype.prefix, urltype.title))
        fields.insert(0, forms.ChoiceField(label=_("Type URL"), choices=choices))

        # Instantiate widget. Is not done by parent at all.
        widget = self.widget(url_type_registry=url_type_registry)
        kwargs['widget'] = widget
        super(AnyUrlField, self).__init__(fields, *args, **kwargs)


    def compress(self, data_list):
        if data_list:
            type_prefix = data_list[0]    # avoid `id, *values = data_list` notation, that is python 3 syntax.
            values = data_list[1:]

            # May happen when deleting models in formsets
            if type_prefix is None or type_prefix == '':
                return None

            urltype = self.url_type_registry[type_prefix]
            value_index = self.url_type_registry.index(type_prefix)
            value = values[value_index]

            if type_prefix == 'http':
                return AnyUrlValue(type_prefix, value, self.url_type_registry)
            else:
                if urltype.has_id_value:
                    if isinstance(value, Model):
                        value = value.pk   # Auto cast foreign keys to integer.
                    elif value:
                        value = long(value)
                    else:
                        return None
                return AnyUrlValue(type_prefix, value, self.url_type_registry)
        return None


    def clean(self, value):
        # Get the value
        # Totally replaced validation.
        clean_data = []
        errors = ErrorList()

        # Only the visible field is required.
        radio_value = value[0]
        field_visible = [False] * len(self.fields)
        field_visible[0] = True
        if radio_value is None:
            # radio_value is None when models are deleted in formsets
            out = ''
        else:
            field_visible[self.url_type_registry.index(radio_value) + 1] = True

            # The validators only fire for visible fields.
            for i, field in enumerate(self.fields):
                try:
                    field_value = value[i]
                except IndexError:
                    field_value = None

                if not field_visible[i]:
                    clean_data.append(None)
                    continue

                if self.required and field_value in validators.EMPTY_VALUES:
                    raise ValidationError(self.error_messages['required'])

                try:
                    clean_data.append(field.clean(field_value))
                except ValidationError, e:
                    errors.extend(e.messages)  # Collect all widget errors
            if errors:
                raise ValidationError(errors)

            out = self.compress(clean_data)

        self.validate(out)
        return out
