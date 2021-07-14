from datetime import datetime, timedelta

import pytest
from django.test import TestCase

from tests.models import *

data_org = {"name": "Acme Widgets"}


class FieldTestCase(TestCase):
    def setUp(self):
        self.org = Org.objects.create(**data_org)
        self.created = datetime.now()
        self.one_sec = timedelta(seconds=1)
        pass

    #        org = Org.objects.create(**data_org)

    def test_obj_creation(self):
        assert self.one_sec > self.created - self.org.created
        assert self.one_sec > self.created - self.org.updated

    def test_updated(self):
        self.org.name = "Updated"
        self.org.save()

        now = datetime.now()
        assert self.one_sec > self.created - self.org.created
        assert self.one_sec > now - self.org.updated
