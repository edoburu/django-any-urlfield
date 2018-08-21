from django import forms
from django.core.cache import cache
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from any_urlfield import EXTERNAL_SCHEMES
from any_urlfield.cache import get_object_cache_keys
from any_urlfield.forms.fields import ExtendedURLField


class UrlType(object):

    def __init__(self, model, form_field, widget, title, prefix, has_id_value):
        if form_field is None:
            # Generate default form field if nothing is provided.
            if has_id_value:
                form_field = lambda: forms.ModelChoiceField(queryset=model._default_manager.all(), widget=widget)
            else:
                form_field = forms.CharField(widget=widget)

        self.model = model
        self.form_field = form_field
        self.title = title
        self.prefix = prefix
        self.has_id_value = has_id_value

    def __repr__(self):
        return "<UrlType {0}>".format(self.prefix)

    def __getstate__(self):
        # Can't pickle lambda or callable values, so force evaluation
        dict = self.__dict__.copy()
        dict['form_field'] = self.get_form_field()
        return dict

    def __eq__(self, other):
        if not isinstance(other, UrlType):
            return NotImplemented

        # Skipping title and form_field
        return self.model == other.model \
            and self.prefix == other.prefix \
            and self.has_id_value == other.has_id_value

    def __ne__(self, other):
        return not self == other

    def get_form_field(self):
        """
        Create the form field for the URL type.
        """
        if callable(self.form_field):
            return self.form_field()
        else:
            return self.form_field

    def get_widget(self):
        """
        Create the widget for the URL type.
        """
        form_field = self.get_form_field()
        widget = form_field.widget
        if isinstance(widget, type):
            widget = widget()

        # Widget instantiation needs to happen manually.
        # Auto skip if choices is not an existing attribute.
        form_field_choices = getattr(form_field, 'choices', None)
        if form_field_choices is not None:
            if hasattr(widget, 'choices'):
                widget.choices = form_field_choices
        return widget


class UrlTypeRegistry(object):
    """
    Registration backend to administrate the various types.
    """

    def __init__(self):
        self._url_types = [UrlType(
            model=None,
            form_field=ExtendedURLField(label=_("External URL"), widget=forms.TextInput(attrs={'class': 'vTextField'})),
            widget=None,
            title=_("External URL"),
            prefix='http',   # no https needed, 'http' is a special constant.
            has_id_value=False
        )]

    def register(self, ModelClass, form_field=None, widget=None, title=None, prefix=None, has_id_value=True):
        """
        Register a custom model with the ``AnyUrlField``.
        """
        if any(urltype.model == ModelClass for urltype in self._url_types):
            raise ValueError("Model is already registered: '{0}'".format(ModelClass))

        opts = ModelClass._meta
        opts = opts.concrete_model._meta

        if not prefix:
            # Store something descriptive, easier to lookup from raw database content.
            prefix = '{0}.{1}'.format(opts.app_label, opts.object_name.lower())
        if not title:
            title = ModelClass._meta.verbose_name

        if self.is_external_url_prefix(prefix):
            raise ValueError("Invalid prefix value: '{0}'.".format(prefix))
        if self[prefix] is not None:
            raise ValueError("Prefix is already registered: '{0}'".format(prefix))
        if form_field is not None and widget is not None:
            raise ValueError("Provide either a form_field or widget; use the widget parameter of the form field instead.")

        urltype = UrlType(ModelClass, form_field, widget, title, prefix, has_id_value)
        signals.post_save.connect(_on_model_save, sender=ModelClass)
        self._url_types.append(urltype)
        return urltype

    def is_external_url_prefix(self, prefix):
        return prefix in EXTERNAL_SCHEMES

    def __eq__(self, other):
        if not isinstance(other, UrlTypeRegistry):
            return NotImplemented

        # For __getstate__ logic
        return self._url_types == other._url_types

    def __ne__(self, other):
        return not self == other

    # Accessing API is similar to `list` and '`dict`:

    def __iter__(self):
        return iter(self._url_types)

    def get_for_model(self, ModelClass):
        """
        Return the URL type for a given model class
        """
        for urltype in self._url_types:
            if urltype.model is ModelClass:
                return urltype
        return None

    def __getitem__(self, prefix):
        # Any web domain will be handled by the standard URLField.
        if self.is_external_url_prefix(prefix):
            prefix = 'http'

        for urltype in self._url_types:
            if urltype.prefix == prefix:
                return urltype
        return None

    def index(self, prefix):
        """
        Return the model index for a prefix.
        """
        # Any web domain will be handled by the standard URLField.
        if self.is_external_url_prefix(prefix):
            prefix = 'http'

        for i, urltype in enumerate(self._url_types):
            if urltype.prefix == prefix:
                return i
        return None

    def keys(self):
        """
        Return the available url type prefixes.
        """
        return [urltype.prefix for urltype in self._url_types]


def _on_model_save(instance, **kwargs):
    """
    Called when a model is saved.
    """
    cache.delete_many(get_object_cache_keys(instance))
