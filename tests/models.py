
from django.db import models
from django_handleref.models import HandleRefModel


class Org(HandleRefModel):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = u'peeringdb_organization'
        verbose_name_plural = "Organizations"

    class HandleRef:
        delete_cascade = ["widget_set",]
        tag = 'org'
        pass

    def __unicode__(self):
        return self.name

class Widget(HandleRefModel):
    name = models.CharField(max_length=255, unique=True)

    class HandleRef:
        custom_option = "passthrough"
