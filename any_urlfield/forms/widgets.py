"""
Custom widgets used by the URL form fields.
"""
from __future__ import unicode_literals
import django
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel
from django.forms import widgets
from django.forms.util import flatatt
from django.forms.widgets import RadioFieldRenderer
from django.template.defaultfilters import slugify
try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode
from django.utils.safestring import mark_safe


class HorizontalRadioFieldRenderer(RadioFieldRenderer):
    """
    Render a :class:`~django.forms.RadioSelect` horizontally in the Django admin interface.

    This produces a similar layout like the ``radio_fields = {'field': admin.HORIZONTAL}`` code does in the admin interface.
    It can be used as argument for the :class:`~django.forms.RadioSelect` widget:

    .. code-block:: python

        widget = widgets.RadioSelect(choices=choices, renderer=HorizontalRadioFieldRenderer)
    """
    def __init__(self, name, value, attrs, choices):
        extraclasses = 'radiolist inline'
        if 'class' in attrs:
            attrs['class'] += ' ' + extraclasses
        else:
            attrs['class'] = extraclasses

        super(HorizontalRadioFieldRenderer, self).__init__(name, value, attrs, choices)

    def render(self):
        return mark_safe(u'<ul%s>\n%s\n</ul>' % (
            flatatt(self.attrs),
            u'\n'.join([u'<li>%s</li>' % force_unicode(w) for w in self]))
        )


class AnyUrlWidget(widgets.MultiWidget):
    """
    The URL widget, rendering the URL selector.
    """

    class Media:
        js = ('any_urlfield/any_urlfield.js',)
        css = {'all': ('any_urlfield/any_urlfield.css',)}


    def __init__(self, url_type_registry, attrs=None):
        type_choices = [(urltype.prefix, urltype.title) for urltype in url_type_registry]

        # Expose sub widgets for form field.
        self.url_type_registry = url_type_registry
        self.url_type_widget = widgets.RadioSelect(choices=type_choices, attrs={'class': 'any_urlfield-url_type'}, renderer=HorizontalRadioFieldRenderer)
        self.url_widgets = []

        # Combine to list, ensure order of values list later.
        subwidgets = []
        for urltype in url_type_registry:
            widget = urltype.get_widget()
            subwidgets.append(widget)

        subwidgets.insert(0, self.url_type_widget)

        # init MultiWidget base
        super(AnyUrlWidget, self).__init__(subwidgets, attrs=attrs)


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
                values[value.type_prefix] = value.type_value

        # Append all values in the proper ordering
        for urltype in self.url_type_registry:
            result.append(values.get(urltype.prefix, None))

        return result

    if django.VERSION < (1, 6, 0):
        def _has_changed(self, initial, data):
            if initial is None:
                initial = [u'http', u'', u'', u'']
            return super(AnyUrlWidget, self)._has_changed(initial, data)


    def format_output(self, rendered_widgets):
        """
        Custom rendering of the widgets.
        """
        urltypes = list(self.url_type_registry)
        url_type_html = rendered_widgets.pop(0)
        output = [ url_type_html ]

        # Wrap remaining options in <p> for scripting.
        for i, widget_html in enumerate(rendered_widgets):
            prefix = slugify(urltypes[i].prefix)  # can use [i], same order of adding items.
            output.append(u'<p class="any_urlfield-url-{0}" style="clear:left">{1}</p>'.format(prefix, widget_html))

        return u''.join(output)


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
        if django.VERSION >= (1, 6, 0):
            rel = ManyToOneRel(None, model, model._meta.pk.name, limit_choices_to=limit_choices_to)
        else:
            rel = ManyToOneRel(model, model._meta.pk.name, limit_choices_to=limit_choices_to)

        if django.VERSION < (1,4):
            super(SimpleRawIdWidget, self).__init__(rel=rel, attrs=attrs, using=using)
        else:
            # admin_site was added in Django 1.4, fixing the popup URL for the change list.
            # Also default to admin.site, allowing a more auto-configuration style.
            if admin_site is None:
                admin_site = admin.site
            super(SimpleRawIdWidget, self).__init__(rel=rel, admin_site=admin_site, attrs=attrs, using=using)
