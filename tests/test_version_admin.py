import pytest
from django.urls import reverse


def _test_view_object_history(org, versions, user, client):
    opts = org._meta
    url = reverse("admin:%s_%s_history" % (opts.app_label, opts.model_name),args=(org.id,))

    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert u"{}".format(response.content).find("Version History") > -1

    for version in versions:
        assert u"{}".format(response.content).find("history/{}".format(version.id))


def _test_view_version_details(org, versions, user, client):
    opts = org._meta

    for version in versions:
        url = reverse("admin:%s_%s_version" % (opts.app_label, opts.model_name),args=(org.id, version.id))
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert u"{}".format(response.content).find("Snapshot") > -1


def _test_view_version_revert(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse("admin:%s_%s_version_revert" % (opts.app_label, opts.model_name),args=(org.id,))
    response = client.get(url, {"version_id":version_b.id}, follow=True)
    assert response.status_code == 200
    assert u"{}".format(response.content).find("Preview Reversion") > -1


def _test_view_version_revert_process(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse("admin:%s_%s_version_revert_process" % (opts.app_label, opts.model_name),args=(org.id,))
    response = client.post(url, {"field_name":version_a.id}, follow=True)
    assert response.status_code == 200

    org.refresh_from_db()
    assert org.name == "Test"



def _test_view_version_rollback(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse("admin:%s_%s_version_rollback" % (opts.app_label, opts.model_name),args=(org.id,version_a.id))
    response = client.get(url, {"version_id":version_b.id}, follow=True)
    assert response.status_code == 200
    assert u"{}".format(response.content).find("Confirm Rollback") > -1


def _test_view_version_rollback_process(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse("admin:%s_%s_version_rollback_process" % (opts.app_label, opts.model_name),args=(org.id,version_a.id))
    response = client.post(url,{}, follow=True)
    assert response.status_code == 200

    org.refresh_from_db()
    assert org.name == "Test"




# TEST WITH REVERSION AS VERSIONING BACKEND

@pytest.mark.django_db
def test_view_object_history(db, superuser, reversion_org):
    _test_view_object_history(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_version_details(db, superuser, reversion_org):
    _test_view_version_details(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_version_revert(db, superuser, reversion_org):
    _test_view_version_revert(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_version_revert_process(db, superuser, reversion_org):
    _test_view_version_revert_process(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_version_rollback(db, superuser, reversion_org):
    _test_view_version_rollback(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_version_rollback_process(db, superuser, reversion_org):
    _test_view_version_rollback_process(*reversion_org, **superuser)
