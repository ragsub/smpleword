from django import forms
from django.core.validators import RegexValidator

alpha = RegexValidator(r'^[a-zA-Z]*$', 'Only alphabets allowed.')

class WordleForm(forms.Form):
    word = forms.CharField(
        max_length=5, 
        min_length=5,
        label='Enter word',
        validators=[alpha],
        widget = forms.TextInput (
            attrs = ({
                'autofocus':'autofocus',
                'size':5,
                'pattern':'[A-Za-z]+',
                'title':'Only alphabets',
                'class':'form-control-sm'
            })
        )
    )

    attempts_left = forms.IntegerField(
        max_value=6,
        initial=6,
        required = False,
        widget = forms.NumberInput(
            attrs = ({
                'readonly':'readonly',
                'style':'width:6ch',
                'class':'bg-light form-control-sm'
            })
        )
    )

    target_word = forms.CharField(
        required=False,
        widget = forms.HiddenInput()
    )
    
class WordForm(forms.Form):
    w = forms.CharField (required=False, initial='xxxxx', widget = forms.HiddenInput())
    l1 = forms.CharField(required = False, initial='bg-light text-secondary', widget = forms.HiddenInput())
    l2 = forms.CharField(required = False, initial='bg-light text-secondary', widget = forms.HiddenInput())
    l3 = forms.CharField(required = False, initial='bg-light text-secondary',widget = forms.HiddenInput())
    l4 = forms.CharField(required = False, initial='bg-light text-secondary',widget = forms.HiddenInput())
    l5 = forms.CharField(required = False, initial='bg-light text-secondary',widget = forms.HiddenInput())

class AlphabetForm(forms.Form):
    letter = forms.CharField(required = False, initial='bg-light text-secondary', widget = forms.HiddenInput())