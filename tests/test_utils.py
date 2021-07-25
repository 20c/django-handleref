import pytest

from django_handleref import util


def test_split_ref():
    assert ("asdf", 123) == util.split_ref("asdf123")
    assert ("asdf", 123) == util.split_ref("ASDF123")
    assert ("asdf", 123) == util.split_ref("asdf 123")
    assert ("asdf", 123) == util.split_ref("asdf-123")


def test_split_ref_exc():
    with pytest.raises(ValueError):
        util.split_ref("asdf123a")
    with pytest.raises(ValueError):
        util.split_ref("123asdf")
