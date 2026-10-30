import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files import File

class Beneficiaire(models.Model):
    utilisateur = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code_interne = models.CharField(max_length=50, unique=True)
    filiere = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.utilisateur.first_name} {self.utilisateur.last_name} - {self.code_interne}"

class TypeAttestation(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField()
    modele_fichier = models.FileField(upload_to='modeles/', blank=True, null=True)
    
    def __str__(self):
        return self.libelle

class DemandeAttestation(models.Model):
    STATUT_CHOICES = (
        ('ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('REJETEE', 'Rejetée'),
    )
    beneficiaire = models.ForeignKey(Beneficiaire, on_delete=models.CASCADE)
    type_demande = models.ForeignKey(TypeAttestation, on_delete=models.CASCADE)
    date_depot = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ATTENTE')
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Demande {self.id} - {self.beneficiaire} ({self.get_statut_display()})"

class Attestation(models.Model):
    demande = models.OneToOneField(DemandeAttestation, on_delete=models.CASCADE)
    numero_unique = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fichier_pdf = models.FileField(upload_to='attestations/', blank=True, null=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    est_valide = models.BooleanField(default=True)
    
    # NEW FIELD: Store the QR code
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"Attestation {self.numero_unique}"

    def save(self, *args, **kwargs):
        # Generate the QR code automatically when saving a new Attestation
        if not self.qr_code:
            # The URL the QR code will point to when scanned by an employer
            domain = 'http://192.168.11.107:8000' #laptop domain
            verification_url = f"{domain}/verify/{self.numero_unique}/"

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            # Save it using the UUID so the filename is secure
            filename = f'qr_{self.numero_unique}.png'
            self.qr_code.save(filename, File(buffer), save=False)
            
        super().save(*args, **kwargs)

class JournalAction(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100) # 'SOUMISSION', 'VALIDATION', 'REJET'
    date_heure = models.DateTimeField(auto_now_add=True)
    objet_concerne = models.CharField(max_length=255) # 'Demande #12'
    detail = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date_heure.strftime('%Y-%m-%d %H:%M')} - {self.action} par {self.utilisateur}"