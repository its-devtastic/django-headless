import uuid
from typing import Literal

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from headless.fields import TagField
from headless.models import ContentModel
from . import forms


def generate_uuid(instance, filename):
    return str(uuid.uuid4())


class CropField(models.JSONField):
    description = "A field for storing crop information."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", list)
        kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)


class Media(ContentModel):
    class Meta(ContentModel.Meta):
        db_table = "headless_media"
        verbose_name = _("Media")
        verbose_name_plural = _("Media")

    file = models.FileField(upload_to=generate_uuid, verbose_name=_("File"))

    name = models.CharField(
        blank=True, default="", max_length=255, verbose_name=_("Name")
    )

    alt_text = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name=_("Alt tekst"),
        help_text=_("Describes a picture for screen readers"),
    )

    tags = TagField(verbose_name=_("Tags"))

    folder = models.ForeignKey(
        "Folder",
        null=True,
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name=_("Folder"),
    )

    crop = CropField(verbose_name=_("Crop"))

    size = models.PositiveIntegerField(
        null=True, verbose_name=_("File size"), editable=False
    )

    type = models.CharField(
        choices={
            "image": _("Image"),
            "video": _("Video"),
            "audio": _("Audio"),
            "file": _("File"),
        },
        default="file",
        verbose_name=_("File type"),
        max_length=20,
    )

    def __str__(self):
        return self.file.url

    def save(self, *args, **kwargs):
        if not self.name:
            file_name = self.file.name.split("/")[-1]
            # If file name has an extension
            if "." in file_name:
                # Remove extension
                self.name = ".".join(file_name.split(".")[:-1])
            else:
                self.name = file_name

        self.size = round(self.file.size / 1000)

        return super().save(*args, **kwargs)


class Folder(ContentModel):
    class Meta(ContentModel.Meta):
        db_table = "headless_folder"
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")
        unique_together = ("name", "parent")

    name = models.CharField(
        max_length=100, verbose_name=_("Name"), validators=[MinLengthValidator(1)]
    )

    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


type FileType = Literal["video", "image", "audio", "file"]


class BaseMediaField:
    """
    Base class for all media fields.
    """

    file_type: FileType | list[FileType] = None
    form_class = None

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["file_type"] = self.file_type
        return name, path, args, kwargs

    def formfield(self, form_class=None, **kwargs):
        return super().formfield(
            **{
                "form_class": self.form_class,
                "file_type": self.file_type,
                **kwargs,
            }
        )


class MediaField(BaseMediaField, models.ForeignKey):
    """
    Single media item model field.
    """

    form_class = forms.MediaField

    def __init__(self, file_type: FileType | list[FileType] = None, **kwargs):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("related_name", "+")
        kwargs.setdefault("on_delete", models.SET_NULL)
        kwargs.setdefault("null", True)

        kwargs.pop("to", None)

        if file_type:
            self.file_type = file_type

        super().__init__(to="headless_media_library.Media", **kwargs)


class ManyMediaField(BaseMediaField, models.ManyToManyField):
    """
    Many media items model field.
    """

    form_class = forms.ManyMediaField

    def __init__(self, file_type: FileType | list[FileType] = None, **kwargs):
        kwargs.setdefault("blank", True)
        kwargs.setdefault("related_name", "+")

        kwargs.pop("to", None)

        if file_type:
            self.file_type = file_type

        super().__init__(to="headless_media_library.Media", **kwargs)
