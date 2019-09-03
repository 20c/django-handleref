from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.base import RedirectView

# auto admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/',  include(admin.site.urls)),
]
