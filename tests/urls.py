from django.conf import settings
from django.conf.urls import include, re_path
from django.conf.urls.static import static

# auto admin
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.autodiscover()

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
]
