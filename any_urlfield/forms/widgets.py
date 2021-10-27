"""
Custom widgets used by the URL form fields.
"""

import re

from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ManyToOneRel
from django.forms import widgets
from django.forms.utils import flatatt
from django.template.defaultfilters import slugify
from django.urls import reverse, NoReverseMatch  # Django 1.10+
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import Truncator


RE_CLEANUP_CLASS = re.compile('[^a-z0-9-_]')


class UrlTypeSelect(widgets.RadioSelect):
    """
    Horizontal radio select
    """
    template_name = "any_urlfield/widgets/url_type_select.html"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].setdefault('class', 'any_urlfield-url_type radiolist inline')
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['flatatt'] = flatatt(context['widget']['attrs'])
        return context


class AnyUrlWidget(widgets.MultiWidget):
    """
    The URL widget, rendering the URL selector.
    """
    template_name = 'any_urlfield/widgets/any_urlfield.html'

    class Media:
        js = ('any_urlfield/any_urlfield.js',)
        css = {'all': ('any_urlfield/any_urlfield.css',)}

    def __init__(self, url_type_registry, attrs=None):
        type_choices = [(urltype.prefix, urltype.title) for urltype in url_type_registry]

        # Expose sub widgets for form field.
        self.url_type_registry = url_type_registry
        self.url_type_widget = UrlTypeSelect(choices=type_choices)
        self.url_widgets = []

        # Combine to list, ensure order of values list later.
        subwidgets = []
        for urltype in url_type_registry:
            widget = urltype.get_widget()
            subwidgets.append(widget)

        subwidgets.insert(0, self.url_type_widget)

        # init MultiWidget base
        super().__init__(subwidgets, attrs=attrs)

    def decompress(self, value):
        # Split the value to a dictionary with key per prefix.
        # value is a AnyUrlValue object
        result = [None]
        values = {}
        if value is None:
            values['http'] = ''
            result[0] = 'http'
        else:
            # Expand the AnyUrlValue to the array of widget values.
            # This is the reason, the widgets are ordered by ID; to make this easy.
            result[0] = value.type_prefix
            if value.type_prefix == 'http':
                values['http'] = value.type_value
            else:
                # Instead of just passing the ID, make sure our SimpleRawIdWidget
                # doesn't have to perform a query while we already have prefetched data.
                values[value.type_prefix] = value.bound_type_value

        # Append all values in the proper ordering,
        # for every registered widget type shown in this multiwidget.
        for urltype in self.url_type_registry:
            result.append(values.get(urltype.prefix, None))

        return result

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # BEGIN Django 1.11 code!
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            widget_name = '{}_{}'.format(name, i)
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = '{}_{}'.format(id_, i)
            else:
                widget_attrs = final_attrs

            # FIX Django 1.11 "bug" of lost context for fields!
            subwidgets.append(widget.get_context(widget_name, widget_value, widget_attrs))
        context['widget']['subwidgets'] = subwidgets
        # END

        # Each subwidget corresponds with an registered URL type.
        # Make sure the template can render the proper ID's for JavaScript.
        for i, urltype in enumerate(self.url_type_registry):
            subwidgets[i + 1]['prefix'] = RE_CLEANUP_CLASS.sub('', urltype.prefix)

        return context


class SimpleRawIdWidget(ForeignKeyRawIdWidget):
    """
    A wrapper class to create raw ID widgets.

    It produces a same layout as the ``raw_id_fields = (field',)`` code does in the admin interface.
    This class wraps the functionality of the Django admin application
    into a usable format that is both compatible with Django 1.3 and 1.4.

    The basic invocation only requires the model:

    .. code-block:: python

        widget = SimpleRawIdWidget(MyModel)
    """

    def __init__(self, model, limit_choices_to=None, admin_site=None, attrs=None, using=None):
        """
        Instantiate the class.
        """
        if admin_site is None:
            admin_site = admin.site
        rel = ManyToOneRel(None, model, model._meta.pk.name, limit_choices_to=limit_choices_to)
        super().__init__(rel=rel, admin_site=admin_site, attrs=attrs, using=using)

    def label_and_url_for_value(self, value):
        """Optimize retrieval of the data.
        Because AnyUrlField.decompose() secretly returns both the ID,
        and it's prefetched object, there is no need to refetch the object here.
        """
        try:
            obj = value.prefetched_object  # ResolvedTypeValue
        except AttributeError:
            return super().label_and_url_for_value(value)

        # Standard Django logic follows:
        try:
            url = reverse(
                '{admin}:{app}_{model}_change'.format(
                    admin=self.admin_site.name,
                    app=obj._meta.app_label,
                    model=obj._meta.object_name.lower()
                ),
                args=(obj.pk,)
            )
        except NoReverseMatch:
            url = ''  # Admin not registered for target model.

        return Truncator(obj).words(14, truncate='...'), url
