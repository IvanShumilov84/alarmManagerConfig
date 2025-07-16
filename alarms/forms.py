from django import forms
from django.core.exceptions import ValidationError
from .models import AlarmConfig, AlarmTable


class AlarmTableForm(forms.ModelForm):
    """Форма для создания и редактирования таблиц аварий"""

    class Meta:
        model = AlarmTable
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название таблицы",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Введите описание таблицы",
                }
            ),
        }


class AlarmConfigForm(forms.ModelForm):
    """Форма для создания и редактирования конфигураций аварий"""

    class Meta:
        model = AlarmConfig
        fields = [
            "alarm_class",
            "table",
            "logic",
            "channel",
            "limit_type",
            "limit_config_type",
            "low",
            "high",
            "discrete_val",
            "msg",
            "hyst_low",
            "hyst_high",
            "ch_low",
            "ch_high",
            "confirm_method",
            "prior",
        ]
        widgets = {
            "alarm_class": forms.Select(attrs={"class": "form-control"}),
            "table": forms.Select(attrs={"class": "form-control"}),
            "logic": forms.Select(attrs={"class": "form-control"}),
            "channel": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите имя канала"}
            ),
            "limit_type": forms.Select(attrs={"class": "form-control"}),
            "limit_config_type": forms.Select(attrs={"class": "form-control"}),
            "low": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "high": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "discrete_val": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "msg": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Введите текст сообщения",
                }
            ),
            "hyst_low": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "hyst_high": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "ch_low": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите канал нижнего предела",
                }
            ),
            "ch_high": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите канал верхнего предела",
                }
            ),
            "confirm_method": forms.Select(attrs={"class": "form-control"}),
            "prior": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "1000"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["low"].required = False
        self.fields["high"].required = False
        # Устанавливаем empty_label для ForeignKey полей
        self.fields["alarm_class"].empty_label = "---------"
        self.fields["logic"].empty_label = "---------"
        self.fields["confirm_method"].empty_label = "---------"
        self.fields["limit_type"].empty_label = "---------"
        self.fields["limit_config_type"].empty_label = "---------"

    def clean(self):
        cleaned_data = super().clean()
        logic = cleaned_data.get("logic")
        # channel = cleaned_data.get('channel')
        limit_type = cleaned_data.get("limit_type")
        limit_config_type = cleaned_data.get("limit_config_type")

        def is_empty(val):
            return val in [None, ""]

        # Удалена ручная валидация channel, чтобы не блокировать остальные ошибки

        if logic and logic.name == "analog":
            if not limit_type:
                self.add_error("limit_type", "Обязательное поле.")
            low = cleaned_data.get("low")
            high = cleaned_data.get("high")
            ch_low = cleaned_data.get("ch_low")
            ch_high = cleaned_data.get("ch_high")

            if limit_config_type and limit_config_type.name == "values":
                if limit_type and limit_type.name not in ["low", "low_high"]:
                    cleaned_data["low"] = 0
                if limit_type and limit_type.name not in ["high", "low_high"]:
                    cleaned_data["high"] = 0
                cleaned_data["ch_low"] = ""
                cleaned_data["ch_high"] = ""
                if (
                    limit_type
                    and limit_type.name in ["low", "low_high"]
                    and is_empty(low)
                ):
                    self.add_error("low", "Обязательное поле.")
                if (
                    limit_type
                    and limit_type.name in ["high", "low_high"]
                    and is_empty(high)
                ):
                    self.add_error("high", "Обязательное поле.")
            elif limit_config_type and limit_config_type.name == "channels":
                if limit_type and limit_type.name not in ["low", "low_high"]:
                    cleaned_data.pop("ch_low", None)
                if limit_type and limit_type.name not in ["high", "low_high"]:
                    cleaned_data.pop("ch_high", None)
                cleaned_data["low"] = 0
                cleaned_data["high"] = 0
                if (
                    limit_type
                    and limit_type.name in ["low", "low_high"]
                    and is_empty(ch_low)
                ):
                    self.add_error("ch_low", "Обязательное поле.")
                if (
                    limit_type
                    and limit_type.name in ["high", "low_high"]
                    and is_empty(ch_high)
                ):
                    self.add_error("ch_high", "Обязательное поле.")
            else:
                cleaned_data["low"] = 0
                cleaned_data["high"] = 0
                cleaned_data["ch_low"] = ""
                cleaned_data["ch_high"] = ""

        return cleaned_data

    def clean_low(self):
        limit_type = self.data.get("limit_type")
        limit_config_type = self.data.get("limit_config_type")
        if (
            self.cleaned_data.get("logic")
            and self.cleaned_data.get("logic").name == "analog"
            and limit_config_type
            and limit_config_type == "1"  # ID для "values"
        ):
            if limit_type and limit_type not in ["1", "3"]:  # ID для "low" и "low_high"
                return 0
        return self.cleaned_data.get("low")

    def clean_high(self):
        limit_type = self.data.get("limit_type")
        limit_config_type = self.data.get("limit_config_type")
        if (
            self.cleaned_data.get("logic")
            and self.cleaned_data.get("logic").name == "analog"
            and limit_config_type
            and limit_config_type == "1"  # ID для "values"
        ):
            if limit_type and limit_type not in [
                "2",
                "3",
            ]:  # ID для "high" и "low_high"
                return 0
        return self.cleaned_data.get("high")

    def clean_ch_low(self):
        value = self.cleaned_data.get("ch_low")
        return value if value is not None else ""

    def clean_ch_high(self):
        value = self.cleaned_data.get("ch_high")
        return value if value is not None else ""
