from django.core.exceptions import ValidationError

try:
    import reversion
except ImportError:
    reversion = None


class Version:

    """
    Object version interface - extend to support
    different types of django object versioning
    solutions
    """

    def __init__(self, version):

        """
        Argument(s):

            - version: version object instance, for example
                django reversion Version object

        """
        self.version = version

    @property
    def date(self):
        """
        Should return version date (datetime object)
        """
        raise NotImplementedError()

    @property
    def user(self):
        """
        Should return user (django User object) that commited the version
        or None if no such user exists
        """
        raise NotImplementedError()

    @property
    def id(self):
        """
        Should return the internal version id (primary
        key in the database)
        """
        raise NotImplementedError()

    @property
    def comment(self):
        """
        Should return comment (str) for the version
        or None if no such comment exists
        """
        raise NotImplementedError()

    @property
    def data(self):
        """
        Should return a dict of the object snapshot
        store in this version, with field names mapping
        to field values
        """
        raise NotImplementedError()

    @property
    def data_sorted(self):
        """
        Should return `data` in list form with (field, value)
        tuples as items, sorted by field
        """
        raise NotImplementedError()

    @property
    def model(self):
        """
        Should return the django model class of the object
        snapshotted by the version
        """
        raise NotImplementedError()

    @property
    def previous(self):
        """
        Should return a Version instance holding the previous
        version neighbour of this version

        If no previous version exists return an empty Version
        instance
        """
        raise NotImplementedError()

    @property
    def next(self):
        """
        Should return a Version instance holding the next
        version neighbour of this version

        if no next version exists return an empty Version
        instance
        """
        raise NotImplementedError()

    @classmethod
    def changes_summary(self, versions):
        """
        Compiles and return a changes summary of multiple
        Version objects.

        Argument(s):

            - versions(list): list of Version instances

        Returns:

            - list: a list of (field, dict) tuples where
                the dict will be mapping version ids to a
                dict containing changes made to the field
                by the version. Check `Diff` class for
                further information

        """

        changes = {}
        for version in versions:
            _changes = version.changes(version.previous)
            for field, diff in _changes.items():
                if field not in changes:
                    changes[field] = {}
                _diff = {"version": version}
                _diff.update(diff)
                changes[field].update({version.id: _diff})
        changes_list = list(changes.items())
        changes_list = sorted(changes_list, key=lambda i: i[0])
        return changes_list

    def changes(self, previous):
        """
        Return a `Diff` instance for this version
        and a previous version

        Argument(s):

            - previous(Version)

        Returns(s):

            - Diff

        """

        return Diff(previous, self).changes

    def changed_fields(self, previous):

        """
        Return a list of changed fields between
        this version and a previous version

        Argument(s):

            - previous(Version)

        Returns:

            - list(str)

        """

        changes = self.changes(previous)
        if changes is None:
            return None
        return sorted(changes.keys())


class ReversionVersion(Version):

    """
    Version abtraction for django-reversion
    """

    def __init__(self, version):
        """
        Argument(s):

            - Version(int|reversion.models.Version): can be either
                a reversion version instance or the id of one

        """
        if isinstance(version, int):
            version = reversion.models.Version.objects.get(id=version)
        super().__init__(version)

    @property
    def date(self):
        """
        Returns:

            - datetime: date of revision

        """
        return self.version.revision.date_created

    @property
    def user(self):
        """
        Returns:

            - User: user that authored revision
            - None: if no such user exists

        """
        return self.version.revision.user

    @property
    def comment(self):
        """
        Returns:

            - str: comment stored with revision
            - None: if no such comment exists

        """
        return self.version.revision.comment

    @property
    def id(self):
        """
        Returns:

            - int:version instance id

        """
        return self.version.id

    @property
    def data(self):
        """
        Returns:

            - dict: object data

        """
        return self.version.field_dict

    @property
    def model(self):
        """
        Returns:

            - model: django model for the object
                snapshotted by this version

        """
        return self.version._model

    @property
    def data_sorted(self):
        """
        Returns:

            - list: list of (field, value) tuples for
                object data

        """
        data = []

        for field, value in self.data.items():
            data.append((field, value))

        return sorted(data, key=lambda i: i[0])

    @property
    def previous(self):
        """
        Returns:

            - Version: previous version - if no previous version exists
                the Version instance will be empty

        """

        if hasattr(self, "_previous"):
            return self._previous
        qset = reversion.models.Version.objects.filter(
            content_type_id=self.version.content_type_id,
            object_id=self.version.object_id,
            id__lt=self.version.id,
        )
        qset = qset.order_by("-id")
        self._previous = self.__class__(qset.first())
        return self._previous

    @property
    def next(self):
        """
        Returns:

            - Version: next version - if no next version exists
                the Version instance will be empty

        """

        if hasattr(self, "_next"):
            return self._next
        qset = reversion.models.Version.objects.filter(
            content_type_id=self.version.content_type_id,
            object_id=self.version.object_id,
            id__gt=self.version.id,
        )
        qset = qset.order_by("id")
        self._next = self.__class__(qset.first())
        return self._next


class Diff:

    """
    Describes changes between two versions
    """

    # when generating diff ignore these fields

    diff_ignore_fields = [
        "version",
        "created",
        "updated",
    ]

    def __init__(self, version_a, version_b):

        """
        Argument(s):

            - version_a(Version): older version
            - version_b(Version): newer version

        """

        self.version_a = version_a
        self.version_b = version_b

    @property
    def changes(self):

        """
        Compile and return a dict describing changes between
        the two versions tracked in this diff

        Returns:

            - dict: dict mapping field names to a dict describing
              changed made to the field


              {
                  field_name: {
                      "old": old_value,
                      "changed": changed_value,
                  },
                  ...
              }

        """

        if not self.version_a or not self.version_b:
            return None

        if not self.version_a.version or not self.version_b.version:
            return None

        data_a = self.version_a.data
        data_b = self.version_b.data

        diff = {}

        for field, value_b in data_b.items():
            if field in self.diff_ignore_fields:
                continue

            value_a = data_a.get(field)

            if value_a == value_b:
                continue

            if isinstance(value_a, str) or isinstance(value_a, int):
                diff[field] = {"old": value_a, "changed": value_b}
            else:
                diff[field] = {
                    "old": self.format_value(value_a),
                    "changed": self.format_value(value_b),
                }

        return diff

    def format_value(self, value):
        return f"{value}"


class Reverter:

    """
    Allows to revert / rollback changes
    """

    def revert_fields(self, instance, field_versions, **kwargs):

        """
        Revert a set of fields

        Argument(s):

            - instance(model instance): instance of django model
              to be reverted
            - field_versions(dict): dict mapping field names to
              version object

        Raises:

            - ValidationError: if any of the fields fail validation

        """

        for field, version in field_versions.items():
            setattr(instance, field, version.data[field])
            if field == "status":
                self.validate_status_change(instance, version.data[field])
        instance.full_clean()
        instance.save()

    def rollback(self, instance, version, **kwargs):

        """
        Rollback to a specific version

        Argument(s):

            - instance(model instance): instance of django model
              to be reverted
            - version(Version): version to roll back to

        Raises:

            - ValidationError: if any of the fields fail validation

        """

        for field, value in version.data.items():
            if field in ["created", "updated", "version"]:
                continue
            if field == "status":
                self.validate_status_change(instance, value)
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()

    def validate_status_change(self, instance, status):

        """
        Validate a status value change - this will make sure
        an object cannot be undeleted if a parent relationship
        is still flagged as deleted

        Argument(s):

            - instance(model instance): instance of django model
              to be reverted
            - status(str)

        """

        for field in instance.__class__._meta.get_fields():
            if not field.is_relation or not field.many_to_one:
                continue
            try:
                relation = getattr(instance, field.name)
            except Exception:
                continue
            self.validate_parent_status(instance, relation, status)

    def validate_parent_status(self, instance, parent, status):

        if not hasattr(parent, "HandleRef"):
            return

        if parent.status == "deleted" and status != "deleted":
            raise ValidationError(
                {
                    "non_field_errors": "Parent object {} is currently flagged as deleted."
                    "This object may not be undeleted while the parent "
                    "is still deleted.".format(parent)
                }
            )


class ReversionReverter(Reverter):

    """
    Reverter abstraction for django-reversion
    """

    def revert_fields(self, instance, field_versions, user=None):

        """
        Revert a set of fields

        Argument(s):

            - instance(model instance): instance of django model
              to be reverted
            - field_versions(dict): dict mapping field names to
              version pk

        Keyword Argument(s):

            - user(User): user that authored the revision

        Raises:

            - ValidationError: if any of the fields fail validation

        """

        with reversion.create_revision():
            if user:
                reversion.set_user(user)
            version_ids = [
                "{}".format(version.data["version"])
                for version in field_versions.values()
            ]
            version_ids = list(set(version_ids))
            reversion.set_comment(
                "reverted some fields via versions: {}".format(", ".join(version_ids))
            )
            super().revert_fields(instance, field_versions)

    def rollback(self, instance, version, user=None):

        """
        Rollback to a specific version

        Argument(s):

            - instance(model instance): instance of django model
              to be reverted
            - version(Version): version to roll back to

        Keyword Argument(s):

            - user(User): user that authored the revision

        Raises:

            - ValidationError: if any of the fields fail validation

        """

        with reversion.create_revision():
            if user:
                reversion.set_user(user)
            reversion.set_comment(
                "rollback to version {}".format(version.data["version"])
            )
            super().rollback(instance, version)
