import pytest
from django.conf import settings


@pytest.fixture
def superuser():
    from django.contrib.auth import get_user_model
    from django.test import Client

    user = get_user_model().objects.create_user(
        "superuser", password="test", is_staff=True, is_superuser=True
    )
    client = Client()
    client.login(username="superuser", password="test")
    return {"user": user, "client": client}


@pytest.fixture
def reversion_org():
    import reversion

    from django_handleref.version import ReversionVersion
    from tests.reversion_models import VersionedOrg

    with reversion.create_revision():
        org = VersionedOrg.objects.create(name="Test", status="ok")

    with reversion.create_revision():
        org.name = "Updated"
        org.save()

    with reversion.create_revision():
        org.name = "Again"
        org.website = "http://localhost"
        org.save()

    versions = reversion.models.Version.objects.get_for_object(org).order_by("id")

    return (org, [ReversionVersion(v) for v in versions])


@pytest.fixture
def reversion_org_many():
    import reversion

    from django_handleref.version import ReversionVersion
    from tests.reversion_models import VersionedOrg

    with reversion.create_revision():
        org = VersionedOrg.objects.create(name="Test", status="ok")

    for i in range(0, 150):
        with reversion.create_revision():
            org.name = f"Updated {i}"
            org.save()

    versions = reversion.models.Version.objects.get_for_object(org).order_by("id")

    return (org, [ReversionVersion(v) for v in versions])


def pytest_configure():

    settings.configure(
        ROOT_URLCONF="tests.urls",
        SECRET_KEY="mPqac6DEtYxY-0Mu946UUpg-YDVmXWkYj6L4rIE15_A",
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "django_handleref",
            "reversion",
            "tests",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {},
            }
        ],
        DATABASE_ENGINE="django.db.backends.sqlite3",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        STATIC_URL="static/",
        DEBUG=True,
        TEMPLATE_DEBUG=True,
    )
