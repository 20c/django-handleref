import pytest
from django.urls import reverse


def _test_view_object_history(org, versions, user, client):
    opts = org._meta
    url = reverse(f"admin:{opts.app_label}_{opts.model_name}_history", args=(org.id,))

    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert f"{response.content}".find("Version History") > -1

    for version in versions:
        assert f"{response.content}".find(f"history/{version.id}")


def _test_view_version_details(org, versions, user, client):
    opts = org._meta

    for version in versions:
        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_version",
            args=(org.id, version.id),
        )
        response = client.get(url, follow=True)
        assert response.status_code == 200
        assert f"{response.content}".find("Snapshot") > -1


def _test_view_version_revert(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse(
        f"admin:{opts.app_label}_{opts.model_name}_version_revert", args=(org.id,)
    )
    response = client.get(url, {"version_id": version_b.id}, follow=True)
    assert response.status_code == 200
    assert f"{response.content}".find("Preview Reversion") > -1


def _test_view_version_revert_process(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse(
        f"admin:{opts.app_label}_{opts.model_name}_version_revert_process",
        args=(org.id,),
    )
    response = client.post(url, {"field_name": version_a.id}, follow=True)
    assert response.status_code == 200

    org.refresh_from_db()
    assert org.name == "Test"


def _test_view_version_rollback(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse(
        f"admin:{opts.app_label}_{opts.model_name}_version_rollback",
        args=(org.id, version_a.id),
    )
    response = client.get(url, {"version_id": version_b.id}, follow=True)
    assert response.status_code == 200
    assert f"{response.content}".find("Confirm Rollback") > -1


def _test_view_version_rollback_process(org, versions, user, client):
    opts = org._meta
    version_a, version_b, version_c = versions
    url = reverse(
        f"admin:{opts.app_label}_{opts.model_name}_version_rollback_process",
        args=(org.id, version_a.id),
    )
    response = client.post(url, {}, follow=True)
    assert response.status_code == 200

    org.refresh_from_db()
    assert org.name == "Test"


# TEST WITH REVERSION AS VERSIONING BACKEND


@pytest.mark.django_db
def test_view_object_history(db, superuser, reversion_org):
    _test_view_object_history(*reversion_org, **superuser)

@pytest.mark.django_db
def test_view_object_history_pagination(db, superuser, reversion_org_many):
    _test_view_object_history(*reversion_org_many, **superuser)

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
