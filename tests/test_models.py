
import pytest

from tests.models import *


def test_model_init():
    org = Org()
    assert 'org' == org.ref_tag
    assert 'org' == Org.handleref.tag
    with pytest.raises(ValueError) as e:
        org.handle

    widget = Widget()

    # no tag specified on model, should default to lower-case
    # class name
    assert 'widget' == widget.ref_tag 
    assert 'widget' == Widget.handleref.tag

    assert widget._handleref.custom_option == "passthrough"
    assert Widget.handleref.prop("custom_option") == "passthrough"
