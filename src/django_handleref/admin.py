import logging
import re
import traceback

from django import forms
from django.conf.urls import re_path
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

# soft import reversion - since it is not a hard
# requirement for django-handleref
try:
    import reversion
except ImportError:
    reversion = None

# we only support reversion at this point
from django_handleref.version import ReversionReverter, ReversionVersion

logger = logging.getLogger("django")


class HistoryActionsForm(forms.Form):
    action = forms.ChoiceField(choices=(("revert", _("Revert")),))


class VersionAdmin(admin.ModelAdmin):

    """
    ModelAdmin mixin that will enable handleref version
    history for any model it is attached to
    """

    # admin view templates, grappelli versions exist
    # at "handleref/grappelli/"

    object_history_template = "handleref/object_history.html"
    version_details_template = "handleref/version_details.html"
    version_revert_template = "handleref/version_revert.html"
    version_rollback_template = "handleref/version_rollback.html"

    # which version abstraction to use for operations
    # set to reversion as default

    version_cls = ReversionVersion
    reverter_cls = ReversionReverter

    # display these fields in the object history listing
    # fields starting with the `version_` prefix will
    # automatically redirect to the Version objects property
    #
    # so `version_id` will go to Version.id for example

    version_list_fields = [
        ("version_id", _("Version ID")),
        ("version", _("Version")),
        ("version_date", _("Date")),
        ("version_user", _("User")),
        ("status", _("Object Status")),
        ("version_changes", _("Changes")),
    ]

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta
        info = (
            opts.app_label,
            opts.model_name,
        )
        my_urls = [
            re_path(
                r"^([^/]+)/history/revert/process/$",
                self.admin_site.admin_view(self.version_revert_process),
                name="%s_%s_version_revert_process" % info,
            ),
            re_path(
                r"^([^/]+)/history/revert/$",
                self.admin_site.admin_view(self.version_revert_view),
                name="%s_%s_version_revert" % info,
            ),
            re_path(
                r"^([^/]+)/history/(\d+)/rollback/process/$",
                self.admin_site.admin_view(self.version_rollback_process),
                name="%s_%s_version_rollback_process" % info,
            ),
            re_path(
                r"^([^/]+)/history/(\d+)/rollback/$",
                self.admin_site.admin_view(self.version_rollback_view),
                name="%s_%s_version_rollback" % info,
            ),
            re_path(
                r"^([^/]+)/history/(\d+)/$",
                self.admin_site.admin_view(self.version_details_view),
                name="%s_%s_version" % info,
            ),
        ]
        return my_urls + urls

    def history_query_set(self, object_id):
        """
        Arguments:

            - object_id(int)

        Returns:

            - reversion.models.Version queryset

        """

        instance = self.model.objects.get(pk=object_id)

        # TODO: abstract this away from reversion
        # we are only supporting django-reversion it this point
        # so it's ok for now

        history_qset = reversion.models.Version.objects.get_for_object(instance)
        history_qset = history_qset.order_by("-revision_id")
        return history_qset

    def history_entry(self, version, previous):

        """
        Compile object history list entry dict

        Argument(s):

            - version(handleref.Version.Version): newer version
            - previous(handleref.version.Version): older version
              if no older version exists will be an empty Version instance

        Returns:

            - dict: {"id","fields","comment"}

        """

        fields = []
        entry = {"id": version.id, "fields": fields, "comment": version.comment}

        for field, label in self.version_list_fields:
            if field == "version_changes":
                fields.append((field, version.changes(previous)))
            elif field == "version_changed_fields":
                fields.append((field, version.changed_fields(previous)))
            elif field.find("version_") == 0:
                fields.append((field, getattr(version, field.split("_")[1])))
            else:
                fields.append((field, version.data.get(field, "")))
        return entry

    def history(self, history_qset):
        """
        Compile and return history listing data from history queryset

        Argument(s):

            - history_qset (queryset): queryset of versions

        Returns:

            - list: list containing `history_entry` dicts

        """

        history = []

        versions = [v for v in history_qset]

        versions.reverse()

        # If there are no previous versions, return an empty history
        if not versions:
            return history
        previous = self.version_cls(versions[0]).previous

        for _version in versions:
            version = self.version_cls(_version)
            history.insert(0, self.history_entry(version, previous))
            previous = version

        return history

    def history_view(self, request, object_id):

        """
        object history view
        """

        # require superuser

        if not request.user.is_superuser:
            return redirect("admin:login")

        action = request.POST.get("action")

        # if action is set to revert, it means one or more versions
        # have been selected to preview for revert so redirect to
        # reversion version view

        if action == "revert":
            return self.version_revert_view(request, object_id)

        history_qset = self.history_query_set(object_id)
        listing = HistoryListing(self, request, history_qset)
        history = self.history(listing.result_list)

        context = dict(
            self.admin_site.each_context(request),
            object_id=object_id,
            model=self.model,
            action_form=HistoryActionsForm(),
            history=history,
            history_qset=history_qset,
            listing=listing,
            version_list_fields=self.version_list_fields,
            field_count=len(self.version_list_fields),
            title=_("Version History"),
        )

        return super().history_view(request, object_id, context)

    def version_details_view(self, request, object_id, version_id, extra_context=None):

        """
        Show version details
        """

        # require superuser

        if not request.user.is_superuser:
            return redirect("admin:login")

        version = self.version_cls(reversion.models.Version.objects.get(id=version_id))
        previous = version.previous
        context = dict(
            self.admin_site.each_context(request),
            object_id=object_id,
            version_id=version_id,
            instance=self.model.objects.get(id=object_id),
            opts=self.model._meta,
            version=version,
            previous=previous,
            changes=version.changes(previous),
        )
        context.update(extra_context or {})
        return TemplateResponse(request, self.version_details_template, context)

    def version_revert_view(self, request, object_id, extra_context=None):

        """
        Show version revert preview / confiformation view
        """

        # require superuser

        if not request.user.is_superuser:
            return redirect("admin:login")

        version_ids = request.GET.getlist(
            "version_id", request.POST.getlist("version_id", [])
        )
        if not isinstance(version_ids, list):
            version_ids = [version_ids]
        versions = [
            self.version_cls(reversion.models.Version.objects.get(id=version_id))
            for version_id in version_ids
        ]

        changes = self.version_cls.changes_summary(versions)

        context = dict(
            self.admin_site.each_context(request),
            object_id=object_id,
            instance=self.model.objects.get(id=object_id),
            opts=self.model._meta,
            versions=versions,
            count=len(versions),
            changes=changes,
        )
        context.update(extra_context or {})
        return TemplateResponse(request, self.version_revert_template, context)

    def version_revert_process(self, request, object_id, extra_context=None):

        """
        Process revert version(s)
        """

        # require superuser

        if not request.user.is_superuser:
            return redirect("admin:login")

        # compile field versions from request args
        # by looking for any arg that has the `field_`
        # prefix - treat their values as version pks

        field_versions = {}

        for key, value in request.POST.items():
            m = re.match("field_(.+)", key)
            if not m:
                continue
            if not int(value):
                continue
            field_versions[m.group(1)] = self.version_cls(int(value))

        errors = {}
        try:

            # revert

            reverter = self.reverter_cls()
            instance = self.model.objects.get(pk=object_id)
            reverter.revert_fields(instance, field_versions, user=request.user)

        except ValidationError as exc:

            # validation errors are collected

            errors = exc.message_dict

        except Exception as exc:

            # any other errors are logged

            errors = {"non_field_errors": ["Internal Error (check server logs)"]}
            logger.error(traceback.format_exc(exc))

        # if there were errors we want to show the revert preview again
        # and include error information

        if errors:
            return self.version_revert_view(
                request, object_id, extra_context={"errors": errors}
            )

        opts = self.model._meta

        # on success return to the object history view

        return redirect(
            "{}:{}_{}_history".format(
                self.admin_site.name, opts.app_label, opts.model_name
            ),
            instance.id,
        )

    def version_rollback_view(self, request, object_id, version_id, extra_context=None):

        """
        Version rollback preview / confirmation view
        """

        # require superuser

        if not request.user.is_superuser:
            return redirect("admin:login")

        version = self.version_cls(int(version_id))

        context = dict(
            self.admin_site.each_context(request),
            object_id=object_id,
            instance=self.model.objects.get(id=object_id),
            opts=self.model._meta,
            version=version,
        )
        context.update(extra_context or {})
        return TemplateResponse(request, self.version_rollback_template, context)

    def version_rollback_process(
        self, request, object_id, version_id, extra_context=None
    ):

        """
        Version rollback process
        """

        # require super user

        if not request.user.is_superuser:
            return redirect("admin:login")

        version = self.version_cls(int(version_id))

        errors = {}
        try:

            # rollback

            reverter = self.reverter_cls()
            instance = self.model.objects.get(pk=object_id)
            reverter.rollback(instance, version, user=request.user)

        except ValidationError as exc:

            # collect validation errors

            errors = exc.message_dict

        except Exception as exc:

            # log any other errors

            errors = {"non_field_errors": ["Internal Error (check server logs)"]}
            logger.error(traceback.format_exc(exc))

        # if there were errors show the rollback preview / confirmation
        # view again with error information

        if errors:
            return self.version_rollback_view(
                request, object_id, version_id, extra_context={"errors": errors}
            )

        opts = self.model._meta

        # on success return to object history

        return redirect(
            "{}:{}_{}_history".format(
                self.admin_site.name, opts.app_label, opts.model_name
            ),
            instance.id,
        )


class HistoryListing(ChangeList):

    """
    History listing view derived from how django admin does it's
    ChangeList. This is mostly so we can support pagination
    """

    def __init__(self, model_admin, request, qset):
        try:
            self.page_num = int(request.GET.get("p", 1))
        except ValueError:
            self.page_num = 1

        self.list_per_page = 100
        self.paginator = model_admin.get_paginator(request, qset, self.list_per_page)

        result_count = self.paginator.count
        self.show_all = False
        self.can_show_all = False
        self.result_count = result_count
        self.full_result_count = qset.count()
        self.multi_page = result_count > self.list_per_page

        self.result_list = self.paginator.page(self.page_num).object_list

        self.params = dict(request.GET.items())
        if "p" in self.params:
            del self.params["p"]
        if "e" in self.params:
            del self.params["e"]
