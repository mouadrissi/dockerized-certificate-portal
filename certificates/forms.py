from django import forms
from .models import DemandeAttestation

class DemandeForm(forms.ModelForm):
    class Meta:
        model = DemandeAttestation
        fields = ['type_demande', 'commentaire'] 
        
        widgets = {
            'type_demande': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Précisez le motif de votre demande (optionnel)'}),
        }
        labels = {
            'type_demande': 'Type d\'attestation souhaitée',
            'commentaire': 'Commentaire / Motif',
        }