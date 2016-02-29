
import pytest

from django.test import TestCase

from tests.models import *


class ModelTests(TestCase):
    

    def test_model_init(self):
        org = Org()
        self.assertEqual('org', org.ref_tag)
        self.assertEqual('org', Org.handleref.tag)
        with self.assertRaises(ValueError) as e:
            org.handle

        widget = Widget()

        # no tag specified on model, should default to lower-case
        # class name

        self.assertEqual('widget', widget.ref_tag)
        self.assertEqual('widget', Widget.handleref.tag)

        self.assertEqual('passthrough', widget._handleref.custom_option)
        self.assertEqual('passthrough', Widget.handleref.prop("custom_option"))

    def test_soft_delete(self):
        org = Org.objects.create(name="TEST SOFT DELETE", status="ok")
        self.assertEqual(org.status, "ok")
        org.delete()
        org.refresh_from_db()
        self.assertEqual(org.status, "deleted")


    def test_hard_delete(self):
        org = Org.objects.create(name="TEST HARD DELETE", status="ok")
        self.assertEqual(org.status, "ok")
        org.delete(hard=True)
        with self.assertRaises(Org.DoesNotExist) as e:
            org.refresh_from_db()

       
