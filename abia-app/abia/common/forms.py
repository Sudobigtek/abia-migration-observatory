from django import forms
from abia.accounts.models import State


class LGAChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        active = State.get_active()
        if active:
            choices = [("", "-- Select LGA --")] + [
                (lga.name, lga.name) for lga in active.lgas.all().order_by('name')
            ]
        else:
            choices = [("", "-- Select LGA --")]
        kwargs['choices'] = choices
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)
