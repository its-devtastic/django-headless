import jsonschema
from django.core.validators import RegexValidator
from django.db import models

from .forms import FlexFormField
from .validators import JSONSchemaValidator


class FlexField(models.JSONField):
    description = "A JSON field with automatic validation against a schema."

    json_schema = None

    def __init__(self, schema, *args, **kwargs):
        if not schema:
            raise ValueError("The schema parameter is required.")

        try:
            jsonschema.validators.validator_for(schema).check_schema(schema)
        except jsonschema.SchemaError:
            raise ValueError("Not a valid JSON schema.")

        self.json_schema = schema

        kwargs["validators"] = [JSONSchemaValidator(json_schema=self.json_schema)]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["schema"] = self.json_schema
        return name, path, args, kwargs

    def formfield(self, form_class=None, **kwargs):
        return super().formfield(
            **{
                "form_class": FlexFormField,
                "json_schema": self.json_schema,
                "encoder": self.encoder,
                "decoder": self.decoder,
                **kwargs,
            }
        )


class URLPathField(models.CharField):
    description = "A field for a URL path. Only accepts letters, numbers, underscores, hyphens and slashes."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("unique", True)
        kwargs.setdefault("max_length", 120)
        kwargs.setdefault(
            "validators",
            [
                RegexValidator(
                    "^[a-zA-Z0-9_/-]+$",
                    message="Only accepts letters, numbers, underscores, hyphens and slashes.",
                ),
                RegexValidator(
                    "//",
                    inverse_match=True,
                    message="Consecutive slashes are not allowed.",
                ),
            ],
        )

        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Make sure paths start with a slash and do not end with one.
        """
        value: str = getattr(model_instance, self.attname, "")

        if not value.startswith("/"):
            value = f"/{value}"

        if value.endswith("/"):
            value = value[:-1]

        setattr(model_instance, self.attname, value)

        return value


class MultipleChoiceField(models.JSONField):
    description = "A field for storing multiple choices as a JSON array."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", list)
        kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)

class TagField(models.JSONField):
    description = "A field for storing tags as a JSON array."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", list)
        kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)