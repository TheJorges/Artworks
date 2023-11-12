from django import forms
from .models import Collection

class CollectionForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=80, required=True)
    description = forms.CharField(label="Descripción", required=True)

    
class AgregarAColeccionForm(forms.Form):
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        required=False,
        empty_label="Todas las colecciones"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['collection'].queryset = Collection.objects.filter(owner=user)