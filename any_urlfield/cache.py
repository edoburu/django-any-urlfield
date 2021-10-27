from django.conf import settings
from django.utils.translation import get_language

_ALL_LANGUAGE_CODES = [code for code, title in settings.LANGUAGES]


def get_urlfield_cache_key(model, pk, language_code=None):
    """
    The low-level function to get the cache key for a model.
    """
    return 'anyurlfield.{}.{}.{}.{}'.format(model._meta.app_label, model.__name__, pk, language_code or get_language())


def get_object_cache_keys(instance):
    """
    Return the cache keys associated with an object.
    """
    if not instance.pk or instance._state.adding:
        return []

    keys = []
    for language in _get_available_languages(instance):
        keys.append(get_urlfield_cache_key(instance.__class__, instance.pk, language))

    return keys


def _get_available_languages(instance):
    try:
        return instance.get_available_languages()  # django-parler
    except AttributeError:
        return _ALL_LANGUAGE_CODES
