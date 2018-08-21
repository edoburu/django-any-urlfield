import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from any_urlfield import EXTERNAL_SCHEMES

try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse


class ExtendedURLValidator(URLValidator):
    """
    Add more schemes to those that will pass validation.
    """
    schemes = URLValidator.schemes + list(EXTERNAL_SCHEMES)

    # Phone numbers don't match the host regex in Django's validator,
    # so we test for a simple alternative.
    tel_re = r'^[0-9\#\*\-\.\(\)\+]+$'

    def __call__(self, value):
        try:
            super(ExtendedURLValidator, self).__call__(value)
        except ValidationError:
            parsed = urlparse(value)
            if parsed.scheme == "tel" and re.match(self.tel_re, parsed.netloc):
                return
            raise
