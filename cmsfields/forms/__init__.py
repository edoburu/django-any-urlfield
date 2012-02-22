from cms.models.pagemodel import Page
from django.utils.translation import ugettext_lazy as _

URL_TYPE_EXTERNAL = 0
URL_TYPE_CMSPAGE = 1
URL_TYPE_ARTICLE = 2

# This is stage 1 to make the page types configurable.
# Stage 2 is making it truely generic.
# Currently the link types are still hard coded in the fields/widgets.

URL_TYPE_SETTINGS = {
    URL_TYPE_EXTERNAL: {
        'title': _("Externe URL"),
        'model': None,
        'prefixes': ['http', 'https'],
    },
    URL_TYPE_CMSPAGE: {
        'title': _("Interne pagina"),
        'model': Page,
        'prefixes': ['pageid'],
    },
    URL_TYPE_ARTICLE: {
        'title': _("Artikel"),
        'model': 'articles.Article',   # avoid circular reference.
        'prefixes': ['articleid'],
    },
}

URL_TYPE_CHOICES = [(k, v['title']) for k, v in URL_TYPE_SETTINGS.iteritems()]
