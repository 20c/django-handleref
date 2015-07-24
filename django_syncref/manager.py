from django.db import models
import datetime

class SyncRefQuerySet(models.QuerySet):
    
    """
    Custom queryset to provide syncref querying
    """

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

            if type(timestamp) in [int, long, float]:
                timestamp = datetime.datetime.fromtimestamp(timestamp)
            
            qset = qset.filter(
                models.Q(created__gt=timestamp) | 
                models.Q(updated__gt=timestamp)
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




class SyncRefManager(models.Manager):

    """
    Custom manager to provide syncref querying 
    """

    def get_queryset(self):
        return SyncRefQuerySet(self.model, using=self._db)

    def since(self, **kwargs):
        return self.get_queryset().since(**kwargs)
