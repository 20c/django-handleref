from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

# auto admin
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = [
    url(r"^admin/", admin.site.urls),
]
