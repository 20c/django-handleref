import time

import pytest
from django.test import TestCase

from tests.models import Org, Sub, Widget


class ManagerTests(TestCase):
    """
    Test handle-ref manager functionality
    """

    @classmethod
    def setUpTestData(cls):
        cls.initTime = time.time()
        cls.orgs = []
        i = 0
        while i < 10:
            cls.orgs.append(Org.objects.create(name="Org %d" % i))
            i = i + 1

        cls.orgs[8].delete()
        cls.orgs[9].delete(hard=True)

    def test_last_change(self):
        org = self.orgs[8]
        self.assertEqual(Org.handleref.last_change(), org.updated)

    def test_since(self):

        org = self.orgs[0]
        t = time.time()

        # we wait a second, so we have a valid timestamp to query
        time.sleep(1)

        # update the org
        org.name = "Updated name 0"
        org.save()

        # the org we just updated should be only org in the query set
        qset = Org.handleref.since(timestamp=t)
        self.assertEqual(qset.count(), 1)
        self.assertEqual(qset.first().id, org.id)

        # we also want to check that org #8 is in the qset when
        # the deleted parameter is passed as true
        qset = Org.handleref.since(timestamp=self.initTime, deleted=True)
        self.assertIn(self.orgs[8].id, [o.id for o in qset])

        # and that it's missing if we don't
        qset = Org.handleref.since(timestamp=self.initTime, deleted=True)
        self.assertIn(self.orgs[8].id, [o.id for o in qset])

    def test_undeleted(self):
        qset = Org.handleref.undeleted()
        self.assertNotIn(self.orgs[8].id, [o.id for o in qset])
