import datetime
import numbers

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class HandleRefQuerySet(models.QuerySet):

    """
    Custom queryset to provide handleref querying
    """

    def last_change(self):
        """
        queries the database for the most recent time an object was either created or
        updated

        returns datetime or None if db is empty
        """
        try:
            cdt = self.latest("created")
            udt = self.latest("updated")
            # print cdt, udt
            return max(cdt.created, udt.updated)

        except ObjectDoesNotExist:
            return None

    def since(self, timestamp=None, version=None, deleted=False):
        """
        Queries the database for objects updated since timestamp or version

        Arguments:

        timestamp <DateTime=None|int=None> if specified return all objects modified since
        that specified time. If integer is submitted it is treated like a unix timestamp

        version <int=None> if specified return all objects with a version greater
        then the one specified

        deleted <bool=False> if true include soft-deleted objects in the result

        Either timestamp or version needs to be provided
        """

        qset = self

        if timestamp is not None:

            if isinstance(timestamp, numbers.Real):
                timestamp = datetime.datetime.fromtimestamp(timestamp)

            qset = qset.filter(
                models.Q(created__gt=timestamp) | models.Q(updated__gt=timestamp)
            )

        if version is not None:

            qset = qset.filter(version__gt=version)

        if not deleted:

            qset = qset.undeleted()

        return qset

    def undeleted(self):

        """
        Only return objects that are not soft-deleted
        """

        return self.exclude(status="deleted")


class HandleRefManager(models.Manager):

    """
    Custom manager to provide handleref querying
    """

    @property
    def tag(self):
        return self.prop("tag")

    def prop(self, key):
        """
        Convenience function for retrieving properties off the
        HandleRef class instance on the model
        """

        return getattr(self.model._handleref, key)

    def get_queryset(self):
        return HandleRefQuerySet(self.model, using=self._db)

    def last_change(self, **kwargs):
        return self.get_queryset().last_change(**kwargs)

    def since(self, **kwargs):
        return self.get_queryset().since(**kwargs)

    def undeleted(self):
        return self.get_queryset().undeleted()
