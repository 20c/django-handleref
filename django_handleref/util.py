
import re


def split_ref(string):
    """ splits a string into (tag, id) """
    re_tag = re.compile('^(?P<tag>[a-zA-Z]+)[\s-]*(?P<pk>\d+)$')
    m = re_tag.search(string)
    if not m:
        raise ValueError("unable to split string '%s'" % (string,))

    return (m.group('tag').lower(), int(m.group('pk')))


