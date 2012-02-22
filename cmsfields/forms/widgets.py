"""
Custom widgets used by the CMS form fields.
"""
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.db.models.fields.related import ManyToOneRel
from django.forms import widgets
from django.forms.util import flatatt
from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from cmsfields.forms import URL_TYPE_CHOICES, URL_TYPE_EXTERNAL, URL_TYPE_CMSPAGE, URL_TYPE_ARTICLE


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


    def __init__(self, attrs=None):
        # Expose sub widgets for form field.
        self.url_type_id_widget = widgets.RadioSelect(choices=URL_TYPE_CHOICES, renderer=HorizonatalRadioFieldRenderer)
        self.url_widget = widgets.TextInput(attrs={'class': 'vTextField'})
        self.page_id_widget = widgets.Select()

        from articles.models import Article
        rel = ManyToOneRel(to=Article, field_name='id')
        self.article_id_widget = ForeignKeyRawIdWidget(rel)

        # Combine to list, ensure order of ID's.
        subwidgets = [None] * 3
        subwidgets[URL_TYPE_EXTERNAL] = self.url_widget
        subwidgets[URL_TYPE_CMSPAGE] = self.page_id_widget
        subwidgets[URL_TYPE_ARTICLE] = self.article_id_widget
        subwidgets.insert(0, self.url_type_id_widget)

        super(CmsUrlWidget, self).__init__(subwidgets, attrs=attrs)

    def decompress(self, value):
        # Split the CmsUrlValue to the multiple widgets
        ids = [None] * len(URL_TYPE_CHOICES)
        if value is None:
            ids[URL_TYPE_EXTERNAL] = ''
            return [URL_TYPE_EXTERNAL] + ids
        else:
            # Expand the CmsUrlValue to the array of widget values.
            # This is the reason, the widgets are ordered by ID; to make this easy.
            if value.url_type_id == URL_TYPE_EXTERNAL:
                ids[URL_TYPE_EXTERNAL] = value.url
            else:
                ids[value.url_type_id] = value.object_id

            return [value.url_type_id] + ids

    def format_output(self, rendered_widgets):
        """
        Custom rendering of the widgets.
        """
        url_type_id_html = rendered_widgets.pop(0)
        output = [ url_type_id_html ]

        # Wrap remaining options in <p> for scripting.
        for i, widget_html in enumerate(rendered_widgets):
            choice = URL_TYPE_CHOICES[i][0]
            output.append(u'<p class="cmsfield-url-{0}" style="clear:left">{1}</p>'.format(choice, widget_html))

        return ''.join(output)
