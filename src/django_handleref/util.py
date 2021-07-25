import re


def split_ref(string):
    """splits a string into (tag, id)"""
    re_tag = re.compile(r"^(?P<tag>[a-zA-Z]+)[\s-]*(?P<pk>\d+)$")
    m = re_tag.search(string)
    if not m:
        raise ValueError(f"unable to split string '{string}'")

    return (m.group("tag").lower(), int(m.group("pk")))
