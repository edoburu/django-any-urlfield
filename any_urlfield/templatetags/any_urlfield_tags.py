"""
Template tags as workaround for a Django 1.11 bug in the multiwidget template.
"""
from django.template import Library, Node, TemplateSyntaxError

register = Library()


class WithDictNode(Node):
    """
    Node to push a complete dict
    """

    def __init__(self, nodelist, context_expr):
        self.nodelist = nodelist
        self.context_expr = context_expr

    def render(self, context):
        """
        Render the tag, with extra context layer.
        """
        extra_context = self.context_expr.resolve(context)
        if not isinstance(extra_context, dict):
            raise TemplateSyntaxError("{% withdict %} expects the argument to be a dictionary.")

        with context.push(**extra_context):
            return self.nodelist.render(context)


@register.tag
def withdict(parser, token):
    """
    Take a complete context dict as extra layer.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("{% withdict %} expects one argument")

    nodelist = parser.parse(('endwithdict',))
    parser.delete_first_token()

    return WithDictNode(
        nodelist=nodelist,
        context_expr=parser.compile_filter(bits[1])
    )
