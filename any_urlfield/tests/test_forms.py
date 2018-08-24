from __future__ import unicode_literals

import django
from django import forms
from django.template import Context, Template
from django.test import TestCase

import any_urlfield.forms
from any_urlfield.forms import SimpleRawIdWidget
from any_urlfield.models import AnyUrlValue
from any_urlfield.models.values import ResolvedTypeValue
from any_urlfield.registry import UrlTypeRegistry
from any_urlfield.tests import PageModel, RegPageModel, UrlModel
from any_urlfield.tests.utils import get_input_values


class FormTests(TestCase):
    """
    Test form rendering and processing.
    """

    maxDiff = None

    def test_form_clean(self):
        """
        Basic test of form validation.
        """
        reg = UrlTypeRegistry()
        reg.register(PageModel)

        class ExampleForm(forms.Form):
            url = any_urlfield.forms.AnyUrlField(url_type_registry=reg)

        # Test 1: basic URL
        form = ExampleForm(data={
            'url_0': 'http',
            'url_1': 'http://examle.org/',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['url'], AnyUrlValue.from_db_value('http://examle.org/'))

        # Test 2: ID field
        x = PageModel.objects.create(slug='foo')
        form = ExampleForm(data={
            'url_0': 'any_urlfield.pagemodel',
            'url_1': '',
            'url_2': str(x.pk),
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['url'].to_db_value(), 'any_urlfield.pagemodel://{}'.format(x.pk))
        self.assertEqual(form.cleaned_data['url'].get_object(), x)

        expected = AnyUrlValue.from_db_value('any_urlfield.pagemodel://{}'.format(x.pk), url_type_registry=reg)
        self.assertEqual(form.cleaned_data['url'], expected)

        # Test 3: invalid ID
        x = PageModel.objects.create(slug='foo')
        form = ExampleForm(data={
            'url_0': 'any_urlfield.pagemodel',
            'url_1': '',
            'url_2': '-1',
        })
        self.assertFalse(form.is_valid())

    def test_modelform(self):
        """
        Testing the model form creation
        """

        class UrlModelForm(forms.ModelForm):
            class Meta:
                model = UrlModel
                fields = ('url',)

        # Test showing the form
        instance = UrlModel.objects.create(url=AnyUrlValue.from_db_value('http://example.org/'))
        form = UrlModelForm(instance=instance)
        self.assertIsInstance(form.fields['url'], any_urlfield.forms.AnyUrlField)
        form.as_p()  # Walk through rendering code.

        # Test saving URLs
        form = UrlModelForm(instance=instance, data={
            'url_0': 'http',
            'url_1': 'http://example2.org/',
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(str(instance.url), 'http://example2.org/')

        # Test saving IDs
        x = RegPageModel.objects.create(slug='modelform')
        form = UrlModelForm(instance=instance, data={
            'url_0': 'any_urlfield.regpagemodel',
            'url_2': str(x.pk),
        })
        self.assertEqual(form.errors, {})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(str(instance.url), '/modelform/')

        # Test showing IDs
        form = UrlModelForm(instance=instance)
        assert form.initial['url'].to_db_value() == 'any_urlfield.regpagemodel://{}'.format(x.pk)
        form.as_p()  # Walk through rendering code.

    def test_render_widget(self):
        """
        See if widget rendering is consistent between Django versions
        """
        reg = UrlTypeRegistry()
        reg.register(PageModel)

        class ExampleForm(forms.Form):
            field = any_urlfield.forms.AnyUrlField(url_type_registry=reg)

        def _normalize_html(html):
            # Avoid some differences in Django versions
            html = html.replace(' checked="checked"', '')
            html = html.replace(' checked', '')
            html = html.replace(' selected="selected"', ' selected')
            html = html.replace(' required', '')
            return html

        html = Template('{{ form.field }}').render(Context({'form': ExampleForm()}))
        self.assertHTMLEqual(_normalize_html(html), _normalize_html("""
    <div class="any-urlfield-wrapper related-widget-wrapper">
      <ul class="any_urlfield-url_type radiolist inline" id="id_field_0">
        <li>
          <label for="id_field_0_0">
            <input type="radio" name="field_0" value="http"
                   class="any_urlfield-url_type radiolist inline" id="id_field_0_0"/>
            External URL</label>
        </li>
        <li>
          <label for="id_field_0_1">
            <input type="radio" name="field_0" value="any_urlfield.pagemodel"
                   class="any_urlfield-url_type radiolist inline" id="id_field_0_1"/>
            page model</label>
        </li>
      </ul>

      <p class="any_urlfield-url-http" style="clear:left">
        <input type="text" name="field_1" class="vTextField" id="id_field_1"/>
      </p>

      <p class="any_urlfield-url-any_urlfieldpagemodel" style="clear:left">
        <select name="field_2" id="id_field_2">
          <option value="" selected>---------</option>
        </select>
      </p>
    </div>
    """))

    def test_raw_id_widget(self):
        """
        Test how the raw ID widget renders.
        """
        from any_urlfield.models import AnyUrlField
        widget = AnyUrlField._static_registry['any_urlfield.regpagemodel'].get_widget()
        self.assertIsInstance(widget, SimpleRawIdWidget)

        html = widget.render(name='NAME', value="111")
        self.assertHTMLEqual(html,
                             '<input class="vForeignKeyRawIdAdminField" name="NAME" type="text" value="111" />'
                             '<a href="/admin/any_urlfield/regpagemodel/?_to_field=id" class="related-lookup"'
                             ' id="lookup_id_NAME" title="Lookup"></a>')

    def test_raw_id_widget_resolved_object(self):
        """
        Test how the raw ID widget renders.
        """
        from any_urlfield.models import AnyUrlField
        widget = AnyUrlField._static_registry['any_urlfield.regpagemodel'].get_widget()
        self.assertIsInstance(widget, SimpleRawIdWidget)

        object = RegPageModel(id=123, slug='OBJ_TITLE')
        value = ResolvedTypeValue(111, prefetched_object=object)

        with self.assertNumQueries(0):
            html = widget.render(name='NAME', value=value)

        if django.VERSION >= (1, 11):
            self.assertHTMLEqual(html,
                                 '<input type="text" name="NAME" value="111" class="vForeignKeyRawIdAdminField">'
                                 '<a href="/admin/any_urlfield/regpagemodel/?_to_field=id" class="related-lookup"'
                                 ' id="lookup_id_NAME" title="Lookup"></a>&nbsp;'
                                 '<strong><a href="/admin/any_urlfield/regpagemodel/123/change/">OBJ_TITLE</a></strong>')
        else:
            self.assertHTMLEqual(html,
                                 '<input type="text" name="NAME" value="111" class="vForeignKeyRawIdAdminField">'
                                 '<a href="/admin/any_urlfield/regpagemodel/?_to_field=id" class="related-lookup"'
                                 ' id="lookup_id_NAME" title="Lookup"></a>&nbsp;'
                                 '<strong>OBJ_TITLE</strong>')

    def test_has_changed_empty_form(self):
        """
        Test that empty placeholder forms are not considered filled in
        """
        reg = UrlTypeRegistry()
        reg.register(PageModel)

        class ExampleForm(forms.Form):
            url = any_urlfield.forms.AnyUrlField(url_type_registry=reg)

        if django.VERSION >= (1, 10):
            empty_kwargs = dict(empty_permitted=True, use_required_attribute=False)
        else:
            empty_kwargs = dict(empty_permitted=True)

        form = ExampleForm(**empty_kwargs)
        data = get_input_values(form.as_p())
        assert form.initial == {}
        assert data == {'url_0': 'http', 'url_1': ''}

        # Submit the values unchanged
        form = ExampleForm(data=data, **empty_kwargs)
        self.assertFalse(form.has_changed(), "form marked as changed!")

    def test_get_input_values(self):
        """
        Test the test code
        """
        html = (
            '<div>\n'
            '<input type="hidden" name="hdn" value="123" />\n'
            '<div>\n'
            '<input type="email" name="email" value="test@example.org" />\n'
            '<input type="checkbox" name="chk" checked="checked" />\n'
            '<input type="checkbox" name="not_chk" />\n'
            '</div>\n'
            '<input type="radio" name="rad" value="1" checked />\n'
            '<input type="radio" name="rad" value="2" />\n'
            '</div>'
        )
        self.assertEqual(get_input_values(html), {
            'hdn': "123",
            'email': "test@example.org",
            'rad': "1",
            'chk': "yes",
        })
