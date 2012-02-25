"""
Custom data objects
"""
from django.db.models.loading import get_model
from django.utils.encoding import StrAndUnicode


class CmsUrlValue(StrAndUnicode):
    """
    Custom value object for the CmsUrlField.

    This value holds both the internal page ID, and external URL.
    Depending on the active value, the URL is automatically generated.
    """
    def __init__(self, url_type_registry, type_prefix, type_value):
        self.url_type_registry = url_type_registry
        self.url_type = self.url_type_registry[type_prefix]
        self.type_value = type_value

        if url_type_registry.index(type_prefix) is None:
            raise ValueError("Unsupported CmsUrlValue prefix: {0}".format(type_prefix))

    @classmethod
    def from_db_value(cls, url_type_registry, url):
        """
        Convert the databse value back to this object.

        Url can be something like:

        * extenal URL: http://.. , https://..
        * custom prefix: customid://214, customid://some/value
        * default prefix: appname.model://31
        """
        try:
            prefix, url_rest = url.split('://', 2)
        except ValueError:
            # While expecting the field to be validated,
            # Don't crash when there is old contents.
            prefix = 'http'
            url_rest = url

        url_type = url_type_registry[prefix]

        if url_type.has_id_value:
            id = int(url_rest)
            return CmsUrlValue(url_type_registry, prefix, id)
        else:
            return CmsUrlValue(url_type_registry, prefix, url)


    def to_db_value(self):
        """
        Convert the value back to something that can be stored in the database.
        For example: http://www.external.url/  or pageid://22
        """
        if self.url_type.prefix == 'http':
            return self.type_value
        else:
            return "{0}://{1}".format(self.url_type.prefix, self.type_value)


    def exists(self):
        if self.url_type.prefix == 'http':
            return True
        elif self.url_type.has_id_value:
            Model = self._get_model()
            return Model.objects.filter(pk=self.type_value).exists()
        elif self.type_value:
            # Random other value that can't be checked
            return True
        else:
            # None or empty.
            return False


    def _get_model(self):
        Model = self.url_type.model
        if isinstance(Model, basestring):
            app_label, model_name = Model.split(".")  # assome appname.ModelName otherwise.
            Model = get_model(app_label, model_name)
        return Model


    @property
    def type_prefix(self):
        return self.url_type.prefix


    def __unicode__(self):
        """
        Return the URL that the value points to.
        """
        if self.url_type.has_id_value:
            Model = self._get_model()
            try:
                object = Model.objects.get(pk=self.type_value)
                return object.get_absolute_url()
            except Model.DoesNotExist:
                return u""
        else:
            return self.type_value or u""


    def __len__(self):
        return len(unicode(self))
