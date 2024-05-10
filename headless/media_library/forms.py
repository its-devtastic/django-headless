from django import forms


class MediaFieldWidget(forms.Select):
    pass


class MediaField(forms.ModelChoiceField):
    file_type = None
    widget = MediaFieldWidget

    def __init__(self, file_type=None, *args, **kwargs):
        self.file_type = file_type

        super().__init__(*args, **kwargs)


class ManyMediaFieldWidget(forms.SelectMultiple):
    pass


class ManyMediaField(forms.ModelMultipleChoiceField):
    file_type = None
    widget = ManyMediaFieldWidget

    def __init__(self, file_type=None, *args, **kwargs):
        self.file_type = file_type

        super().__init__(*args, **kwargs)
