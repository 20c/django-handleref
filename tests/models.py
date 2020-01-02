
from django.db import models
from django_handleref.models import HandleRefModel


class Org(HandleRefModel):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class HandleRef:
        tag = 'org'
        delete_cascade = ["sub_entities"]

    def __unicode__(self):
        return self.name

class Sub(HandleRefModel):
    name = models.CharField(max_length=255, unique=True)
    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="sub_entities")

    class HandleRef:
        tag = 'sub'

    def __unicode__(self):
        return self.name


class Widget(HandleRefModel):
    name = models.CharField(max_length=255, unique=True)

    class HandleRef:
        custom_option = "passthrough"
