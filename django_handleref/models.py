from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_handleref.manager import HandleRefManager

try:
    import reversion

    def handle_version(**kwargs):
        for instance in kwargs.get("instances"):
            instance.version = instance.version + 1
            instance.save()

    reversion.post_revision_commit.connect(handle_version)
except ImportError:
    pass

class HandleRefModel(models.Model):
    
    """
    Provides timestamps for creation and change times,
    versioning (using django-reversion) as well as
    the ability to soft-delete
    """

    id = models.AutoField(primary_key=True)
    status = models.CharField(_('Status'), max_length=255, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    version = models.IntegerField(default=0)

    handleref = HandleRefManager()
    objects = models.Manager()

    class Meta:
        get_latest_by = 'updated'
        ordering = ('-updated', '-created',)
        abstract = True

    @property
    def handle(self):
        if not self._ref_tag:
            self._ref_tag = self.__class__.__name__.lower()
        return self._ref_tag + str(self.id)

    def __unicode__(self):
        if not hasattr(self, "name"): 
          name = self.__class__.__name__
        else:
          name = self.name
        return name + '-' + self.handle

    def delete(self, hard=False):
        
        """
        Override the vanilla delete functionality to soft-delete
        instead. Soft-delete is accomplished by setting the
        status field to "deleted"

        Arguments:

        hard <bool=False> if true, do a hard delete instead, effectively
        removing the object from the database
        """

        if hard:
            return models.Model.delete(self)
        self.status = "deleted"
        self.save()
        if hasattr(self, "delete_cascade"):
            for key in self.delete_cascade:
                for child in getattr(self, key).all():
                    child.delete()


