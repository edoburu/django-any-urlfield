"""
Custom data objects
"""
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.loading import get_model
from django.utils.encoding import StrAndUnicode
import logging

try:
    from django.utils import six
    unicode = six.text_type
    string_types = six.string_types
except ImportError:
    # Python 2, Django 1.3
    string_types = basestring


logger = logging.getLogger('any_urlfield.models')


class AnyUrlValue(StrAndUnicode):
    """
    Custom value object for the :class:`~any_urlfield.models.AnyUrlField`.
    This value holds both the internal page ID, and external URL.
    It can be used to parse the database contents:

    .. code-block:: python

        value = AnyUrlValue.from_db_value(url)
        article = value.get_object()
        print unicode(value)

    A conversion to :class:`unicode` or :class:`str` causes the URL to be generated.
    This allows the field value to be used in string concatenations, or template variable evaluations:

    .. code-block:: html+django

        {{ mymodel.url }}
    """
    def __init__(self, type_prefix, type_value, url_type_registry=None):
        # Easy configuration, allowing other code to deserialize database values.
        if url_type_registry is None:
            from any_urlfield.models.fields import AnyUrlField
            url_type_registry = AnyUrlField._static_registry

        self.url_type_registry = url_type_registry
        self.url_type = url_type_registry[type_prefix]
        self.type_value = type_value

        if url_type_registry.index(type_prefix) is None:
            raise ValueError("Unsupported AnyUrlValue prefix '{0}'. Supported values are: {1}".format(type_prefix, url_type_registry.keys()))


    @classmethod
    def from_db_value(cls, url, url_type_registry=None):
        """
        Convert a serialized database value to this object.

        The value can be something like:

        * an external URL: ``http://..`` , ``https://..``
        * a custom prefix: ``customid://214``, ``customid://some/value``
        * a default "app.model" prefix: ``appname.model://31``
        """
        # Easy configuration, allowing other code to deserialize database values.
        if url_type_registry is None:
            from any_urlfield.models.fields import AnyUrlField
            url_type_registry = AnyUrlField._static_registry

        try:
            prefix, url_rest = url.split('://', 2)
        except ValueError:
            # While expecting the field to be validated,
            # Don't crash when there is old contents.
            prefix = 'http'
            url_rest = url

        url_type = url_type_registry[prefix]
        if url_type is None:
            raise ValueError("Unsupported URL prefix in database value '{0}'. Supported values are: {1}".format(url, url_type_registry.keys()))

        if url_type.has_id_value:
            if url_rest == 'None':
                return None
            id = long(url_rest)
            return AnyUrlValue(prefix, id, url_type_registry)
        else:
            return AnyUrlValue(prefix, url, url_type_registry)


    def to_db_value(self):
        """
        Convert the value into a serialized format which can be stored in the database.
        For example: ``http://www.external.url/``  or ``pageid://22``.
        """
        if self.url_type.prefix == 'http':
            return self.type_value
        elif self.type_value is None:
            return None  # avoid app.model://None
        else:
            return "{0}://{1}".format(self.url_type.prefix, self.type_value)


    def exists(self):
        """
        Check whether the references model still exists.
        """
        if self.url_type.prefix == 'http' and self.type_value:
            return True
        elif self.url_type.has_id_value:
            Model = self.get_model()
            return Model.objects.filter(pk=self.type_value).exists()
        elif self.type_value:
            # Random other value that can't be checked
            return True
        else:
            # None or empty.
            return False


    def get_model(self):
        """
        Return the model that this value points to.
        """
        Model = self.url_type.model
        if isinstance(Model, string_types):
            app_label, model_name = Model.split(".")  # assome appname.ModelName otherwise.
            Model = get_model(app_label, model_name)
        return Model


    def get_object(self):
        """
        Return the database object that the value points to.
        """
        if self.url_type.has_id_value:
            Model = self.get_model()
            return Model.objects.get(pk=self.type_value)
        else:
            return None


    @property
    def type_prefix(self):
        """
        Return the URL type prefix.
        For external URLs this is always ``"http"``.
        """
        return self.url_type.prefix


    # Python 3 support comes from StrAndUnicode
    def __unicode__(self):
        """
        Return the URL that the value points to.
        """
        if self.url_type.has_id_value:
            if not self.type_value:
                return ""

            Model = self.get_model()
            try:
                object = Model.objects.get(pk=self.type_value)
                return object.get_absolute_url()
            except ObjectDoesNotExist as e:
                # Silently fail in templates. Avoid full page crashing.
                logger.exception("Failed to generate URL for {0}".format(repr(self)))
                return "#{0}".format(e.__class__.__name__)
        else:
            return self.type_value or ""


    def __len__(self):
        return len(unicode(self))


    def __repr__(self):
        return str("<AnyUrlValue '{0}'>".format(self.to_db_value()))


    def __getattr__(self, item):
        return getattr(unicode(self), item)


    def __getitem__(self, item):
        return unicode(self).__getitem__(item)


    def __bool__(self):
        return bool(self.type_value)


    # Python 2 support:
    __nonzero__ = __bool__
