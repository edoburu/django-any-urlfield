try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser  # python 2


class InputParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)  # old-style class in Python 2
        self.data = {}

    def handle_starttag(self, tag, attributes):
        if tag == 'input':
            attributes = dict(attributes)
            name = attributes['name']
            type = attributes['type']

            try:
                if type == 'radio':
                    if 'checked' in attributes:
                        self.data[name] = attributes['value']
                elif type == 'checkbox':
                    if 'checked' in attributes:
                        self.data[name] = 'yes'
                else:
                    self.data[name] = attributes.get('value', '')
            except KeyError:
                raise RuntimeError("Faied to parse {tag}: {attributes}".format(tag=tag, attributes=attributes))

    def close(self):
        HTMLParser.close(self)  # python 2
        return self.data


def get_input_values(html):
    """
    Get the input values from a HTML snippet.

    The Python stdlib ElementTree/minidom are all XML based, and can't handle unclosed tags.
    By using HTMLParser instead of html5lib, no external dependencies are needed for testing.
    """
    parser = InputParser()
    parser.feed(html)
    return parser.close()
