from django import forms
from tempus_dominus.widgets import DateTimePicker

class DateTimeForm(forms.Form):
	datetime_field = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )