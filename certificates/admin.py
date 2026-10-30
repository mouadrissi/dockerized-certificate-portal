from django.contrib import admin
from .models import Beneficiaire, TypeAttestation, DemandeAttestation, Attestation

# Registering models to make them visible in the admin dashboard
admin.site.register(Beneficiaire)
admin.site.register(TypeAttestation)
admin.site.register(DemandeAttestation)
admin.site.register(Attestation)