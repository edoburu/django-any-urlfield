"""
Custom form fields for CMS items
"""
from cms.models.pagemodel import Page
from django import forms
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.models import ModelChoiceField
from django.forms.util import ErrorList
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cmsfields.forms import URL_TYPE_CHOICES, URL_TYPE_EXTERNAL, URL_TYPE_CMSPAGE, URL_TYPE_ARTICLE
from cmsfields.forms.widgets import CmsUrlWidget
from cmsfields.models.values import CmsUrlValue


class PageChoiceField(forms.ModelChoiceField):
    """
    A SelectBox that displays the pages QuerySet, with items indented.

    Unlike the standard cms.models.fields.PageField,
    this field does not display a second select box for the site.
    This is easier for single-domain sites.
    """

    def label_from_instance(self, obj):
        page = obj

        # From Django-CMS code:
        page_title = page.get_menu_title(fallback=True)
        if page_title is None:
            page_title = u"page %s" % page.pk
        return mark_safe(u"%s %s" % (u"&nbsp;&nbsp;" * page.level, escape(page_title)))


class CmsUrlFormField(forms.MultiValueField):
    """
    Form field that combines a Page ID and external page URL.
    """
    widget = CmsUrlWidget

    def __init__(self, max_length=None, *args, **kwargs):
        from articles.models import Article  # prevent circular import

        # Build fields,
        # these have to match the widget.
        fields = [None] * 3
        fields[URL_TYPE_EXTERNAL] = forms.URLField(label=_("Externe URL"), required=False, max_length=max_length)
        fields[URL_TYPE_CMSPAGE] = PageChoiceField(label=_("Interne pagina"), required=False, queryset=Page.objects.filter(site=settings.SITE_ID).published())
        fields[URL_TYPE_ARTICLE] = ModelChoiceField(label=_("Artikel"), required=False, queryset=Article.objects.all())
        fields.insert(0, forms.ChoiceField(label=_("Type URL"), choices=URL_TYPE_CHOICES))

        # Instantiate widget. Is not done by parent at all.
        widget = self.widget()
        widget.page_id_widget.choices = fields[URL_TYPE_CMSPAGE +1].choices
        widget.article_id_widget.choices = fields[URL_TYPE_ARTICLE +1].choices
        kwargs['widget'] = widget
        super(CmsUrlFormField, self).__init__(fields, *args, **kwargs)


    def compress(self, data_list):
        if data_list:
            object_type_id = int(data_list[0])    # id, *values = data_list  is python 3 syntax.
            values = data_list[1:]
            if object_type_id == URL_TYPE_EXTERNAL:
                return CmsUrlValue(None, values[object_type_id], object_type_id)
            else:
                return CmsUrlValue(values[object_type_id].pk, None, object_type_id)
        return None


    def clean(self, value):
        # Get the value
        # Totally replaced validation.
        clean_data = []
        errors = ErrorList()

        # Only the visible field is required.
        type_id = int(value[0])
        field_visible = [False] * len(self.fields)
        field_visible[0] = True
        i = 1
        for radio_value, title in URL_TYPE_CHOICES:
            if type_id == radio_value:
                field_visible[i] = True
            i += 1

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
