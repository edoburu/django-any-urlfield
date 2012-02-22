"""
Custom data objects
"""
from django.db import models
from django.db.models.loading import get_model
from django.utils.encoding import StrAndUnicode
from cmsfields.forms import URL_TYPE_SETTINGS, URL_TYPE_CMSPAGE, URL_TYPE_EXTERNAL


class CmsUrlValue(StrAndUnicode):
    """
    Custom value object for the CmsUrlField.

    This value holds both the internal page ID, and external URL.
    Depending on the active value, the URL is automatically generated.
    """
    def __init__(self, object_id, url, url_type_id=URL_TYPE_CMSPAGE):
        self.object_id = int(object_id) if object_id else None
        self.url = str(url) if url else None
        self.url_type_id = int(url_type_id)

        assert url_type_id in URL_TYPE_SETTINGS.keys(), "Invalid url_type_id field"

    @classmethod
    def from_db_value(cls, url):
        """
        Convert the databse value back to this object.

        Url can be something like:
          http://.. , https://..    -> external URL.
          pageid://2                -> CMS page.
          articleid://3             -> Article link.
        """
        try:
            prefix, url_rest = url.split('://', 2)
        except ValueError:
            # While expecting the field to be validated,
            # Don't crash when there is old contents.
            prefix = 'http'
            url_rest = url

        url_type_id = URL_TYPE_EXTERNAL
        url_type = None
        for id, field in URL_TYPE_SETTINGS.iteritems():
            if prefix in field['prefixes']:
                url_type_id = id
                url_type = field
                break
        else:
            raise ValueError("Unsupported CmsUrlValue prefix: " + prefix)

        if url_type['model']:
            id = int(url_rest)
            return CmsUrlValue(id, None, url_type_id)
        else:
            return CmsUrlValue(None, url, url_type_id)


    def to_db_value(self):
        """
        Convert the value back to something that can be stored in the database.
        For example: http://www.external.url/  or pageid://22
        """
        if self.url_type_id == URL_TYPE_EXTERNAL:
            return self.url
        else:
            return "{0}://{1}".format(URL_TYPE_SETTINGS[self.url_type_id]['prefixes'][0], self.object_id)


    def exists(self):
        if self.url_type_id == URL_TYPE_EXTERNAL:
            return True
        elif self.object_id:
            Model = self._get_model()
            return Model.objects.filter(pk=self.object_id).exists()


    def _get_model(self):
        Model = URL_TYPE_SETTINGS[self.url_type_id]['model']  # e.g. Page
        if isinstance(Model, basestring):
            app_label, model_name = Model.split(".")  # assome appname.ModelName otherwise.
            Model = get_model(app_label, model_name)
        return Model


    def __unicode__(self):
        """
        Return the URL that the value points to.
        """
        if self.object_id:
            Model = self._get_model()
            try:
                object = Model.objects.get(pk=self.object_id)
                return object.get_absolute_url()
            except Model.DoesNotExist:
                return u""
        else:
            return self.url or u""


    def __len__(self):
        return len(unicode(self))
