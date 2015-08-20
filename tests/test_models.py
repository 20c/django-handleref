
import pytest

from tests.models import *


def test_model_init():
    org = Org()
    assert 'org' == org._handleref.tag
    assert 'org' == Org.handleref.tag
    with pytest.raises(ValueError) as e:
        org.handle

    widget = Widget()

