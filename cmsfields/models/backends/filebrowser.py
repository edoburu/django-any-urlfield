from __future__ import absolute_import
from filebrowser.fields import FileBrowseField as FileBrowseFieldBase


class FileBrowseField(FileBrowseFieldBase):
    """
    The file browse field based on django-filebrowser.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 100,  # Same as django FileField
            'format': 'Document',
            'directory': kwargs.pop('upload_to', ''),
        }

        defaults.update(kwargs)
        super(FileBrowseField, self).__init__(*args, **defaults)


class ImageBrowseField(FileBrowseField):
    """
    The image browse field based on django-filebrowser.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 100,  # Same as django ImageField
            'format': 'Image',
            'directory': kwargs.pop('upload_to', ''),
        }

        defaults.update(kwargs)
        super(ImageBrowseField, self).__init__(*args, **defaults)
