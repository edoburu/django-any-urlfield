from django import forms
from django.utils.translation import ugettext_lazy as _


# Avoid using common protocol names as prefix, this could clash in the future.
# Values starting with such prefix should be handled as external URL.
_invalid_prefixes = ('http', 'https', 'ftp', 'ftps', 'sftp', 'webdav', 'webdavs', 'afp', 'smb', 'git', 'svn', 'hg')


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
        if getattr(form_field, 'choices', None) and getattr(widget, 'choices', None):
            widget.choices = form_field.choices
        return widget



class UrlTypeRegistry(object):
    """
    Registration backend to administrate the various types.
    """

    def __init__(self):
        self._url_types = [UrlType(
            model=None,
            form_field=forms.URLField(label=_("External URL"), widget=forms.TextInput(attrs={'class': 'vTextField'})),
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
        try:
            opts = opts.concrete_model._meta
        except AttributeError:  # Django 1.3
            pass

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
        self._url_types.append(urltype)
        return urltype


    def is_external_url_prefix(self, prefix):
        return prefix in _invalid_prefixes

    # Accessing API is similar to `list` and '`dict`:

    def __iter__(self):
        return iter(self._url_types)


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
