import sys


if sys.version_info[0] >= 3:
    PY2 = False
    PY3 = True
    string_types = str,
    integer_types = int,
    text_type = str
else:
    PY2 = True
    PY3 = False
    string_types = basestring,
    integer_types = (int, long)
    text_type = unicode


def python_2_unicode_compatible(klass):
    if PY2:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass
