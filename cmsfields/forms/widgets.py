"""
Custom widgets used by the CMS form fields.
"""
from django.forms import widgets
from django.forms.util import flatatt
from django.forms.widgets import RadioFieldRenderer
from django.template.defaultfilters import slugify
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class HorizonatalRadioFieldRenderer(RadioFieldRenderer):
    def __init__(self, name, value, attrs, choices):
        extraclasses = 'radiolist inline cmsfield-url-type'  # last class is not generic!
        if attrs.has_key('class'):
            attrs['class'] += ' ' + extraclasses
        else:
            attrs['class'] = extraclasses

        super(HorizonatalRadioFieldRenderer, self).__init__(name, value, attrs, choices)

    def render(self):
        return mark_safe(u'<ul%s>\n%s\n</ul>' % (
            flatatt(self.attrs),
            u'\n'.join([u'<li>%s</li>' % force_unicode(w) for w in self]))
        )


class CmsUrlWidget(widgets.MultiWidget):
    """
    The widget, rendering the URL selector.
    """

    class Media:
        js = ('cmsfields/cmsurlfield.js',)


    def __init__(self, url_type_registry, attrs=None):
        type_choices = [(urltype.prefix, urltype.title) for urltype in url_type_registry]

        # Expose sub widgets for form field.
        self.url_type_registry = url_type_registry
        self.url_type_widget = widgets.RadioSelect(choices=type_choices, renderer=HorizonatalRadioFieldRenderer)
        self.url_widgets = []

        # Combine to list, ensure order of values list later.
        subwidgets = []
        for urltype in url_type_registry:
            form_field = urltype.form_field
            widget = form_field.widget
            if isinstance(widget, type):
                widget = widget()

            # Widget instantiation needs to happen manually.
            # Auto skip if choices is not an existing attribute.
            if getattr(form_field, 'choices', None) and getattr(widget, 'choices', None):
                widget.choices = form_field.choices

            subwidgets.append(widget)

        subwidgets.insert(0, self.url_type_widget)

        # init MultiWidget base
        super(CmsUrlWidget, self).__init__(subwidgets, attrs=attrs)


    def decompress(self, value):
        # Split the value to a dictionary with key per prefix.
        # value is a CmsUrlValue object
        result = [None]
        values = {}
        if value is None:
            values['http'] = ''
            result[0] = 'http'
        else:
            # Expand the CmsUrlValue to the array of widget values.
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
            output.append(u'<p class="cmsfield-url-{0}" style="clear:left">{1}</p>'.format(prefix, widget_html))

        return u''.join(output)
