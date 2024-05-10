import zoneinfo

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from headless.models import UUIDModel, TimeStampedModel


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        return super().create_user(email, email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return super().create_superuser(email, email, password, **extra_fields)


class User(UUIDModel, AbstractUser, TimeStampedModel):
    class Meta(TimeStampedModel.Meta):
        db_table = "user"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    email = models.EmailField(unique=True, verbose_name=_("Email"))

    profile_picture = models.FileField(
        upload_to="profile_pictures",
        null=True,
        blank=True,
        verbose_name=_("Profile picture"),
    )

    locale = models.CharField(
        choices={"en": "English", "nl": "Dutch"},
        default="en",
        max_length=5,
        verbose_name=_("Locale"),
    )

    timezone = models.CharField(
        choices=sorted([(v, v) for v in zoneinfo.available_timezones()]),
        default="UTC",
        max_length=40,
        verbose_name=_("Timezone"),
    )

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.email
