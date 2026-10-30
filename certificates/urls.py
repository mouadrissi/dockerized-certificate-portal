from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nouvelle-demande/', views.soumettre_demande, name='nouvelle_demande'),

    path('traitement/', views.traitement_demandes, name='traitement_demandes'),
    path('traitement/action/<int:demande_id>/', views.traiter_action, name='traiter_action'),
    path('verification/<uuid:numero_unique>/', views.verifier_attestation, name='verifier_attestation'),

]
