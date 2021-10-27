"""
Custom data objects
"""

import logging

from django.apps import apps
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from any_urlfield.cache import get_urlfield_cache_key


logger = logging.getLogger('any_urlfield.models')

# Not really sure about the cache invalidation yet
URL_CACHE_TIMEOUT = 3600   # 1 hour


class AnyUrlValue:
    """
    Custom value object for the :class:`~any_urlfield.models.AnyUrlField`.
    This value holds both the internal page ID, and external URL.
    It can be used to parse the database contents:

    .. code-block:: python

        value = AnyUrlValue.from_db_value(url)
        article = value.get_object()
        print str(value)

    A conversion to :class:`str` or :class:`str` causes the URL to be generated.
    This allows the field value to be used in string concatenations, or template variable evaluations:

    .. code-block:: html+django

        {{ mymodel.url }}
    """

    def __init__(self, type_prefix, type_value, url_type_registry=None):
        # Easy configuration, allowing other code to deserialize database values.
        if url_type_registry is None:
            from any_urlfield.models.fields import AnyUrlField
            url_type_registry = AnyUrlField._static_registry

        # Note when adding attributes, also add these to __setstate__()
        self.url_type_registry = url_type_registry
        self.url_type = url_type_registry[type_prefix]
        self.type_value = type_value
        self._resolved_objects = None
        self._url_cache = {}

        if url_type_registry.index(type_prefix) is None:
            raise ValueError("Unsupported AnyUrlValue prefix '{}'. Supported values are: {}".format(type_prefix, url_type_registry.keys()))

    @classmethod
    def from_model(cls, model, url_type_registry=None):
        """
        Convert a model value to this object.
        """
        # Easy configuration, allowing other code to deserialize database values.
        if url_type_registry is None:
            from any_urlfield.models.fields import AnyUrlField
            url_type_registry = AnyUrlField._static_registry

        url_type = url_type_registry.get_for_model(model.__class__)
        if url_type is None:
            raise ValueError("Unregistered model for AnyUrlValue: {}".format(model.__class__))

        return cls(url_type.prefix, model.pk, url_type_registry)

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
            raise ValueError("Unsupported URL prefix in database value '{}'. Supported values are: {}".format(url, url_type_registry.keys()))

        if url_type.has_id_value:
            if url_rest == 'None':
                return None
            id = int(url_rest)
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
            return "{}://{}".format(self.url_type.prefix, self.type_value)

    def exists(self):
        """
        Check whether the references model still exists.
        """
        if self.url_type.prefix == 'http' and self.type_value:
            return True
        elif self.url_type.has_id_value:
            if self._resolved_objects is not None:
                # Test whether the in_bulk() found the object
                return self.type_value in self._resolved_objects
            else:
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
        if isinstance(Model, str):
            app_label, model_name = Model.split(".")  # assome appname.ModelName otherwise.
            Model = apps.get_model(app_label, model_name)
        return Model

    def get_object(self):
        """
        Return the database object that the value points to.
        """
        if self.url_type.has_id_value:
            Model = self.get_model()
            if self._resolved_objects is not None:
                try:
                    return self._resolved_objects[self.type_value]
                except KeyError:
                    raise Model.DoesNotExist(
                        "No {} found with ID '{}' by resolve_objects()".format(
                            Model.__class__.__name__, self.type_value
                        )
                    )
            else:
                object = Model.objects.get(pk=self.type_value)
                self._resolved_objects = {self.type_value: object}
                return object
        else:
            return None

    @property
    def type_prefix(self):
        """
        Return the URL type prefix.
        For external URLs this is always ``"http"``.
        """
        return self.url_type.prefix

    @property
    def bound_type_value(self):
        """Keep a reference to the actual object.
        This is a trick for ForeignKeyRawIdWidget, which only receives the integer value.
        Instead of letting it resolve the object, pass the prefetched object here.
        """
        if self._resolved_objects and isinstance(self.type_value, int):
            return ResolvedTypeValue(self.type_value, self._resolved_objects.get(self.type_value))
        return self.type_value

    # Python 2 support comes from python_2_str_compatible
    def __str__(self):
        """
        Return the URL that the value points to.
        """
        if self.url_type.has_id_value:
            if not self.type_value:
                return ""

            # First see if the URL is cached
            cache_key = get_urlfield_cache_key(self.get_model(), self.type_value)
            url = cache.get(cache_key)
            if url:
                return url

            try:
                object = self.get_object()
                url = object.get_absolute_url()
                cache.set(cache_key, url, URL_CACHE_TIMEOUT)
                return url
            except ObjectDoesNotExist as e:
                # Silently fail in templates. Avoid full page crashing.
                logger.error("Failed to generate URL for %r: %s", self, e)
                return "#{}".format(e.__class__.__name__)
        else:
            return self.type_value or ""

    def __len__(self):
        return len(str(self))

    def __repr__(self):
        return str("<AnyUrlValue '{}'>".format(self.to_db_value()))

    def __getattr__(self, item):
        if item[0] == '_':
            # Avoid recursion for missing private fields
            raise AttributeError(item)
        return getattr(str(self), item)

    def __getitem__(self, item):
        return str(self).__getitem__(item)

    def __bool__(self):
        return bool(self.type_value)

    # Python 2 support:
    __nonzero__ = __bool__

    def __eq__(self, other):
        if not isinstance(other, AnyUrlValue):
            return NotImplemented

        return self.url_type == other.url_type \
            and self.type_value == other.type_value

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        """
        Pickle support
        """
        # Avoid pickling the registry if it's the shared one.
        from any_urlfield.models.fields import AnyUrlField
        if self.url_type_registry != AnyUrlField._static_registry:
            url_type_registry = self.url_type_registry
        else:
            url_type_registry = None

        return (url_type_registry, self.url_type.prefix, self.type_value)

    def __setstate__(self, state):
        url_type_registry, prefix, type_value = state

        from any_urlfield.models.fields import AnyUrlField
        if url_type_registry is not None:
            self.url_type_registry = url_type_registry
        else:
            self.url_type_registry = AnyUrlField._static_registry

        self.type_value = type_value
        self.url_type = self.url_type_registry[prefix]
        self._resolved_objects = None
        self._url_cache = {}

    @classmethod
    def resolve_values(cls, values, skip_cached_urls=False):
        """
        Resolve the models for collection of AnyUrlValue objects, to avoid a query per object.
        """
        ids_to_resolve = {}
        values_by_model = {}
        for value in values:
            if value and value.url_type.has_id_value and value._resolved_objects is None:
                Model = value.url_type.model
                if skip_cached_urls and cache.get(get_urlfield_cache_key(Model, value.type_value)):
                    continue

                ids_to_resolve.setdefault(Model, set()).add(value.type_value)
                values_by_model.setdefault(Model, []).append(value)

        for Model, ids in ids_to_resolve.items():
            # When an object can't be found, it simply won't be found in the _resolved_objects dict.
            resolved_objects = Model.objects.in_bulk(ids)
            for value in values_by_model[Model]:
                value._resolved_objects = resolved_objects


class ResolvedTypeValue:
    """
    Keep an ID value associated with the prefetched object.
    This allows code to pass ``AnyUrlField.bound_type_value``
    while the widget rendering still reduces the prefetched object.
    """

    def __init__(self, value, prefetched_object):
        self.value = value
        self.prefetched_object = prefetched_object

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    def __repr__(self):
        return '<ResolvedTypeValue: {}>'.format(self.value)
