import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def generer_attestation_pdf(attestation):
    """
    Génère un PDF avec QR code pour une attestation validée.
    """
    demande = attestation.demande
    beneficiaire = demande.beneficiaire
    utilisateur = beneficiaire.utilisateur

    # 1. Generate the QR Code
    url_verification = f"https://procreate-pantyhose-hypocrite.ngrok-free.dev/verification/{attestation.numero_unique}/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url_verification)
    qr.make(fit=True)
    
    img_qr = qr.make_image(fill_color="black", back_color="white")
    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format="PNG")
    buffer_qr.seek(0)
    qr_reader = ImageReader(buffer_qr)

    # 2. Prepare the PDF
    buffer_pdf = BytesIO()
    p = canvas.Canvas(buffer_pdf, pagesize=A4)
    largeur, hauteur = A4

    # 3 .DESIGN DU PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(2 * cm, hauteur - 3 * cm, "Portail des Attestations")
    
    p.setFont("Helvetica", 10)
    p.drawString(2 * cm, hauteur - 3.7 * cm, "Système de Génération Sécurisée")
    p.line(2 * cm, hauteur - 4 * cm, largeur - 2 * cm, hauteur - 4 * cm)

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(largeur / 2.0, hauteur - 7 * cm, str(demande.type_demande.libelle).upper())

    p.setFont("Helvetica", 12)
    texte_intro = f"Il est certifié par la présente que :"
    p.drawString(2 * cm, hauteur - 10 * cm, texte_intro)

    p.setFont("Helvetica-Bold", 14)
    nom_complet = f"{utilisateur.first_name} {utilisateur.last_name}".upper()
    p.drawString(3 * cm, hauteur - 11.5 * cm, f"Nom & Prénom : {nom_complet}")
    p.drawString(3 * cm, hauteur - 12.5 * cm, f"Code / Matricule : {beneficiaire.code_interne}")
    p.drawString(3 * cm, hauteur - 13.5 * cm, f"Filière : {beneficiaire.filiere}")

    p.setFont("Helvetica", 12)
    texte_fin = "Cette attestation est délivrée pour servir et valoir ce que de droit."
    p.drawString(2 * cm, hauteur - 16 * cm, texte_fin)
    p.drawString(12 * cm, hauteur - 18 * cm, "Fait le : " + attestation.date_generation.strftime("%d/%m/%Y"))

    # 3. Insert the QR Code at the bottom
    p.drawImage(qr_reader, 2 * cm, 2 * cm, width=4*cm, height=4*cm)
    
    p.setFont("Helvetica", 8)
    p.drawString(6.5 * cm, 3.5 * cm, "Pour vérifier l'authenticité de ce document,")
    p.drawString(6.5 * cm, 3 * cm, "veuillez scanner ce code QR ou consulter le portail officiel.")
    p.drawString(6.5 * cm, 2.5 * cm, f"ID unique : {attestation.numero_unique}")

    # Finalize PDF
    p.showPage()
    p.save()
    
    # 4. Save the PDF to the database model
    pdf_val = buffer_pdf.getvalue()
    buffer_pdf.close()
    
    nom_fichier = f"Attestation_{beneficiaire.code_interne}_{attestation.numero_unique}.pdf"
    attestation.fichier_pdf.save(nom_fichier, ContentFile(pdf_val), save=True)