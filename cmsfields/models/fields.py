"""
Custom model fields to link to CMS content.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from cmsfields.models.values import CmsUrlValue
from cmsfields.registry import UrlTypeRegistry


class CmsUrlField(models.CharField):
    """
    A CharField that can either refer to a CMS page ID, or external URL.

    .. figure:: /images/cmsurlfield1.*
       :width: 363px
       :height: 74px
       :alt: CmsUrlField, with external URL input.

    .. figure:: /images/cmsurlfield2.*
       :width: 290px
       :height: 76px
       :alt: CmsUrlField, with internal page input.

    By default, the ``CmsUrlField`` only supports linking to external pages.
    To add support for your own models (e.g. an ``Article`` model),
    include the following code in ``models.py``:

    .. code-block:: python

        from cmsfields.models import CmsUrlField
        CmsUrlField.register_model(Article)

    Now, the ``CmsUrlField`` offers users a dropdown field to directly select an article.
    By default, it uses a ``django.forms.models.ModelChoiceField`` field with a ``django.forms.widgets.Select`` widget
    to render the field.  This can be customized using the ``form_field`` and ``widget`` parameters:

    .. code-block:: python

        from cmsfields.models import CmsUrlField
        from cmsfields.forms.widgets import SimpleRawIdWidget

        CmsUrlField.register_model(Article, widget=SimpleRawIdWidget(Article))

    Now, the ``Article`` model will be displayed as raw input field with a browse button.
    """
    __metaclass__ = models.SubfieldBase
    _static_registry = UrlTypeRegistry()  # Also accessed by CmsUrlValue as internal field.

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('max_length'):
            kwargs['max_length'] = 300
        super(CmsUrlField, self).__init__(*args, **kwargs)


    @classmethod
    def register_model(cls, ModelClass, form_field=None, widget=None, title=None, prefix=None):
        """
        Register a model to use in the URL field.

        This function needs to be called once for every model
        that should be selectable in the URL field.

        :param ModelClass: The model to register.
        :param form_field: The form field class used to render the field.
        :param widget: The widget class, can be used instead of the form field.
        :param title: The title of the model, by default it uses the models ``verbose_name``.
        :param prefix: A custom prefix for the model in the serialized database format. By default it uses "appname.modelname".
        """
        cls._static_registry.register(ModelClass, form_field, widget, title, prefix)


    def formfield(self, **kwargs):
        # Associate formfield.
        # Import locally to avoid circular references.
        from cmsfields.forms.fields import CmsUrlFormField
        kwargs['form_class'] = CmsUrlFormField
        kwargs['url_type_registry'] = self._static_registry
        if kwargs.has_key('widget'):
            del kwargs['widget']
        return super(CmsUrlField, self).formfield(**kwargs)


    def to_python(self, value):
        if isinstance(value, CmsUrlValue):
            return value

        # Convert the string value
        if value is None:
            return None

        return CmsUrlValue.from_db_value(value, self._static_registry)

    def get_prep_value(self, value):
        # Convert back to string
        return value.to_db_value()


    def validate(self, value, model_instance):
        # Final validation of the field, before storing in the DB.
        super(CmsUrlField, self).validate(value, model_instance)
        if value:
            if value.type_prefix == 'http':
                validate_url = URLValidator()
                validate_url(value.type_value)
            elif value.type_value:
                if not value.exists():
                    raise ValidationError(self.error_messages['invalid_choice'] % value.type_value)


# Include the imagefield.
if 'filebrowser' in settings.INSTALLED_APPS:
    from .backends.filebrowser import FileBrowseField, ImageBrowseField
# No sane default CSS:
#elif 'sorl.thumbnail' in settings.INSTALLED_APPS:
#    from .backends.sorl import FileBrowseField, ImageBrowseField
else:
    from .backends.preview import FileBrowseField, ImageBrowseField


# This is included for documentation, consistent south migrations and editor code completion:
class FileBrowseField(FileBrowseField):
    """
    The file browse field based on django-filebrowser, or any other filebrowser.
    It's a drop-in replacement for the django :class:`~django.db.models.FileField`

    When *django-filebrowser* is not installed, it will display the
    standard :class:`~django.db.models.FileField`.
    """


class ImageBrowseField(ImageBrowseField):
    """
    The image browse field based on django-filebrowser, or any other filebrowser.
    It's a drop-in replacement for the django :class:`~django.db.models.ImageField`

    When *django-filebrowser* is not installed, it will display the
    standard :class:`~django.db.models.ImageField` with a preview attached to it.
    """


# Tell South how to create custom fields
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^cmsfields\.models\.fields\.CmsUrlField",
        "^cmsfields\.models\.fields\.FileBrowseField",
        "^cmsfields\.models\.fields\.ImageBrowseField",
        "^cmsfields\.models\.fields\.backends\.([^.]+)\.FileBrowseField",
        "^cmsfields\.models\.fields\.backends\.([^.]+)\.ImageBrowseField",
    ])
except ImportError:
    pass
