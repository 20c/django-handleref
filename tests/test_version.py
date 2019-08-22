import datetime
import pytest

from django_handleref.version import (
    Version,
    Reverter,
    ReversionVersion,
    ReversionReverter,
    Diff,
    )

from tests.reversion_models import VersionedOrg

import reversion

@pytest.mark.parametrize("field",[
    "date",
    "user",
    "id",
    "comment",
    "data",
    "data_sorted",
    "model",
    "previous",
    "next",
])
def test_version_interface(field):

    version = Version(object())

    with pytest.raises(NotImplementedError):
        getattr(version, field)


def _test_changes(org, versions):
    version_a, version_b, version_c = versions
    changes = version_b.changes(version_a)
    assert changes == {'name': {'old': u'Test', 'changed': u'Updated'}}


def _test_changes_summary(org, versions):
    version_a, version_b, version_c = versions
    changes = version_a.changes_summary([version_b, version_c])

    assert changes[0] == ("name", {
        version_b.id : {
            "version" : version_b,
            "old" : u"Test",
            "changed" : u"Updated",
        },
        version_c.id : {
            "version" : version_c,
            "old" : u"Updated",
            "changed" : u"Again",
        }
    })


def _test_changed_fields(org, versions):
    version_a, version_b, version_c = versions
    changed_fields = version_b.changed_fields(version_a)
    assert changed_fields == [u"name"]


def _test_revert_fields(org, versions, reverter):
    version_a, version_b, version_c = versions

    assert org.name == "Again"
    assert org.website == "http://localhost"

    reverter.revert_fields(org, {"name": version_a,
                                 "website": version_b})

    org.refresh_from_db()

    assert org.name == "Test"
    assert org.website == ""


def _test_rollback(org, versions, reverter):
    version_a, version_b, version_c = versions

    reverter = ReversionReverter()

    assert org.name == "Again"
    assert org.website == "http://localhost"

    reverter.rollback(org, version_a)

    org.refresh_from_db()

    assert org.name == "Test"
    assert org.website == ""


# TEST WITH REVERSION AS VERSIONING BACKEND

@pytest.mark.django_db
def test_reversion_version_fields(db):

    with reversion.create_revision():
        org = VersionedOrg.objects.create(name="Test", status="ok")

    org = VersionedOrg.objects.all().first()
    assert org.version == 1

    with reversion.create_revision():
        reversion.set_comment("this is a comment")
        org.name = "Updated"
        org.save()

    org.refresh_from_db()
    assert org.version == 2

    assert reversion.models.Version.objects.all().count() == 2

    version = ReversionVersion(1)

    assert version.id == 1
    assert version.data["name"] == "Test"

    version = version.next

    assert version.id == 2
    assert version.data["name"] == "Updated"
    assert version.comment == "this is a comment"
    assert version.user == None
    assert isinstance(version.date, datetime.datetime)
    assert version.model == VersionedOrg
    assert version.data_sorted == [("created", version.data["created"]),
                                   ("id", 1),
                                   ("name", u"Updated"),
                                   ("notes",u""),
                                   ("status", u"ok"),
                                   ("updated", version.data["updated"]),
                                   ("version", 1),
                                   ("website", u""),
                                   ]

    version = version.previous
    assert version.id == 1



@pytest.mark.django_db
def test_changes(db, reversion_org):
    _test_changes(*reversion_org)


@pytest.mark.django_db
def test_changes_summary(db, reversion_org):
    _test_changes_summary(*reversion_org)


@pytest.mark.django_db
def test_changed_fields(db, reversion_org):
    _test_changed_fields(*reversion_org)


@pytest.mark.django_db
def test_revert_fields(db, reversion_org):
    org, versions = reversion_org
    reverter = ReversionReverter()
    _test_revert_fields(org, versions, reverter)


@pytest.mark.django_db
def test_rollback(db, reversion_org):
    org, versions = reversion_org
    reverter = ReversionReverter()
    _test_rollback(org, versions, reverter)
