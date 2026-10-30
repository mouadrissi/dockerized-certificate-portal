from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('AGENT', 'Agent administratif'),
        ('DEMANDEUR', 'Demandeur / Bénéficiaire'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEMANDEUR')