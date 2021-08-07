from django.db import models
from django.utils.translation import gettext_lazy as _

from django_handleref.manager import HandleRefManager

try:
    import reversion.signals

    def handle_version(**kwargs):
        for vs in kwargs.get("versions"):
            instance = vs.object
            instance.version = instance.version + 1
            instance.save()

    reversion.signals.post_revision_commit.connect(handle_version)
except ImportError:
    pass


class CreatedDateTimeField(models.DateTimeField):
    """DateTimeField that's set to now() on create"""

    def __init__(self, verbose_name=None, name=None, **kwargs):
        if not verbose_name:
            verbose_name = _("Created")

        # force timestamp options
        kwargs["auto_now"] = False
        kwargs["auto_now_add"] = True
        super(models.DateTimeField, self).__init__(verbose_name, name, **kwargs)


class UpdatedDateTimeField(models.DateTimeField):
    """DateTimeField that's set to now() every update"""

    def __init__(self, verbose_name=None, name=None, **kwargs):
        if not verbose_name:
            verbose_name = _("Updated")

        # force timestamp options
        kwargs["auto_now"] = True
        kwargs["auto_now_add"] = False
        super(models.DateTimeField, self).__init__(verbose_name, name, **kwargs)


class HandleRefOptions:
    delete_cascade = []

    def __init__(self, cls, opts):
        if opts:
            for key, value in opts.__dict__.items():
                if key.startswith("__"):
                    continue
                setattr(self, key, value)

        if not getattr(self, "tag", None):
            self.tag = cls.__name__.lower()


class HandleRefMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        # only init subclass
        parents = [b for b in bases if isinstance(b, HandleRefMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new = super_new(cls, name, bases, attrs)
        opts = attrs.pop("HandleRef", None)
        if not opts:
            opts = getattr(new, "HandleRef", None)

        setattr(new, "_handleref", HandleRefOptions(new, opts))
        return new


class HandleRefModel(models.Model, metaclass=HandleRefMeta):
    """
    Provides timestamps for creation and change times,
    versioning (using django-reversion) as well as
    the ability to soft-delete
    """

    id = models.AutoField(primary_key=True)
    status = models.CharField(_("Status"), max_length=255, blank=True)
    created = CreatedDateTimeField()
    updated = UpdatedDateTimeField()
    version = models.IntegerField(default=0)

    handleref = HandleRefManager()
    objects = models.Manager()

    class Meta:
        abstract = True
        get_latest_by = "updated"
        ordering = (
            "-updated",
            "-created",
        )

    @property
    def ref_tag(self):
        if not self._handleref.tag:
            raise ValueError("tag not set")
        return self._handleref.tag

    @property
    def handle(self):
        if not self.id:
            raise ValueError("id not set")
        return self._handleref.tag + str(self.id)

    def __unicode__(self):
        if not hasattr(self, "name"):
            name = self.__class__.__name__
        else:
            name = self.name
        return name + "-" + self.handle

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
        for key in self._handleref.delete_cascade:
            q = getattr(self, key).all()

            if not hard:
                # if we are soft deleting only trigger delete on
                # objects that are not already deleted, as to avoid
                # unnecessary re-saves and overriding of updated dates
                q = q.exclude(status="deleted")

            for child in q:
                child.delete(hard=hard)
