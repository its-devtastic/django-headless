from django import forms


class FlexFieldWidget(forms.MultiWidget):
    schema = None

    def decompress(self, value):
        if isinstance(value, dict):
            return [value.get(key) for key in self.schema["properties"].keys()]

        return []


class FlexFormField(forms.MultiValueField):
    widget = FlexFieldWidget
    schema = None

    widget_mapping = {
        "string": forms.TextInput,
        "number": forms.NumberInput,
        "integer": forms.NumberInput,
        "boolean": forms.CheckboxInput,
    }

    field_mapping = {
        "string": forms.CharField,
        "number": forms.FloatField,
        "integer": forms.IntegerField,
        "boolean": forms.BooleanField,
    }

    def __init__(self, json_schema=None, encoder=None, decoder=None, *args, **kwargs):
        fields = []
        widgets = []
        self.schema = json_schema

        for key, value in json_schema["properties"].items():
            fields.append(self.field_mapping.get(value["type"], forms.CharField)())
            widgets.append(
                self.widget_mapping.get(value["type"], forms.CharField)(
                    {"placeholder": value.get("verbose_name")}
                )
            )

        self.widget = FlexFieldWidget(widgets=widgets)
        self.widget.schema = json_schema
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        output = {}
        for index, key in enumerate(self.schema["properties"].keys()):
            try:
                value = data_list[index]
                if value is not None:
                    output[key] = data_list[index]
            except IndexError:
                pass

        return output
