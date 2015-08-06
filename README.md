# django-handleref
track when an object was created or changed and allow querying based on time and versioning (w/ django-reversion support)

## HandleRefModel as a base for all your models
    
    from django.db import models
    from django_handleref.models import HandleRefModel
    
    class Test(HandleRefModel):
        name = models.CharField(max_length=255)

## Querying for modification since

It is now possible for you to see which instances of a model have been created or modified
since a specific time or version

    import time

    # create instance
    test = Test.objects.create(name="This is a test")

    # keep track of time, we need this later
    t = time.time()

    # modifying and saving it
    test.name = "Changed my mind"
    test.save()

    # now we can use the handleref manager to retrieve it
    Test.handleref.since(timestamp=t).count() # 1
    Test.handleref.since(timestamp=time.time().count() #0


## Soft delete

By default all models extending HandleRefModel will softdelete when their delete() method is called.
Note that this currently wont work for batch deletes - as this does not call the delete() method.

    test = Test.objects.get(id=1)
    test.delete()

    # querying handleref undeleted will not contain the deleted object
    Test.handleref.undeleted().filter(id=1).count() #0

    # querying handleref since will not contain the deleted object
    Test.handleref.since(timestamp=t).filter(id=1).count() #0

    # passing deleted=True to handleref since will contain the deleted object
    Test.handleref.since(timestamp=t, deleted=True).filter(id=1).count() #1

    # querying using the standard objects manager will contain the deleted object
    Test.objects.filter(id=1).count() #1

    # You may also still hard-delete by passing hard=True to delete
    test.delete(hard=True)
    Test.objects.filter(id=1).count() #0

## Versioning (with django-reversion)

Requires 

    django-reversion==1.8.7

When django-reversion is installed all your HandleRefModels will be valid for versioning.

    import reversion

    with reversion.create_revision():
        obj = Test.objects.create(name="This is a test")
        obj.save()
  
        obj.version #1
        
        obj.name = "Changed my mind"
        obj.save()

        obj.version #2

    Test.handleref.since(version=1).count() #1
