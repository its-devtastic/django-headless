from django.db import models
from django.utils.translation import gettext_lazy as _

from headless.models import UUIDModel, TimeStampedModel, EditorModel
from headless.utils import generate_password


class ApiToken(UUIDModel, TimeStampedModel, EditorModel):
    class Meta(TimeStampedModel.Meta):
        db_table = "headless_api_token"
        verbose_name = "API Token"
        verbose_name_plural = "API Tokens"

    token = models.CharField(
        max_length=255,
        unique=True,
        default=generate_password,
        editable=False,
        verbose_name=_("Token"),
    )

    description = models.CharField(
        max_length=120, default="", blank=True, verbose_name=_("Description")
    )

    last_used = models.DateTimeField(
        null=True, editable=False, verbose_name=_("Last used")
    )

    read_only_access = models.BooleanField(default=False, verbose_name=_("Read-only"))

    full_access = models.BooleanField(default=False, verbose_name=_("Full access"))

    permissions = models.ManyToManyField(
        "auth.Permission", related_name="+", blank=True, verbose_name=_("Permissions")
    )

    is_enabled = models.BooleanField(default=True, verbose_name=_("Enabled"))

    def __str__(self):
        return self.description

    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return True

    @property
    def is_superuser(self):
        return self.full_access

    def has_perms(self, perm_list, obj=None):
        if self.full_access:
            return True
        if self.read_only_access:
            return all([perm.split(".")[1].startswith("view_") for perm in perm_list])

        return all(
            [
                self.permissions.filter(
                    codename=perm.split(".")[1],
                    content_type__app_label=perm.split(".")[0],
                ).exists()
                for perm in perm_list
            ]
        )


class ApiTokenUsage(UUIDModel):
    class Meta:
        db_table = "headless_api_token_usage"
        verbose_name = _("API Token Usage")
        verbose_name_plural = _("API Token Usage")
        ordering = ["-timestamp"]

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    method = models.CharField(max_length=10, verbose_name=_("Method"), editable=False)

    path = models.CharField(max_length=255, verbose_name=_("Path"), editable=False)

    query_params = models.CharField(
        max_length=255, default="", verbose_name=_("Query parameters"), editable=False
    )

    token = models.ForeignKey(
        "ApiToken",
        on_delete=models.CASCADE,
        verbose_name=_("Token"),
        related_name="usages",
        editable=False,
    )

    def __str__(self):
        return f"{self.method} {self.path}"
