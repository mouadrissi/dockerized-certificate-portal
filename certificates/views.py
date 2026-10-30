from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DemandeForm
from .models import Beneficiaire, DemandeAttestation, Attestation ,JournalAction
from .utils import generer_attestation_pdf

@login_required
def dashboard(request):
    # Check if the user is a standard student
    if request.user.role == 'DEMANDEUR':
        try:
            demandes = DemandeAttestation.objects.filter(beneficiaire__utilisateur=request.user).order_by('-date_depot')
            stat_attente = demandes.filter(statut='ATTENTE').count()
            stat_validees = demandes.filter(statut='VALIDEE').count()
            context = {
                'demandes': demandes, 
                'stat_attente': stat_attente, 
                'stat_validees': stat_validees,
            }
        except Beneficiaire.DoesNotExist:
            context = {
                'error': "Profil non configuré", 
                'stat_attente': 0, 
                'stat_validees': 0,
            }
            
    else:
        # Show statistics for the whole school (Agents / Admins)
        demandes = DemandeAttestation.objects.all().order_by('-date_depot')
        stat_attente = DemandeAttestation.objects.filter(statut='ATTENTE').count()
        stat_validees = DemandeAttestation.objects.filter(statut='VALIDEE').count()
        context = {
            'stat_attente': stat_attente, 
            'stat_validees': stat_validees, 
            'demandes': demandes,
        }

    return render(request, 'certificates/dashboard.html', context)

@login_required
def soumettre_demande(request):
    try:
        # Check if they have a student profile
        beneficiaire = request.user.beneficiaire
    except Beneficiaire.DoesNotExist:
        # Send an error message and kick them back to the dashboard safely
        messages.error(request, "Votre profil n'est pas encore configuré. Impossible de créer une demande.")
        return redirect('dashboard')

    # If they DO have a profile, show them the form
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.beneficiaire = beneficiaire
            demande.save()
            messages.success(request, "Votre demande a été soumise avec succès !")
            return redirect('dashboard')
    else:
        form = DemandeForm()
        
    return render(request, 'certificates/nouvelle_demande.html', {'form': form})
@login_required
def traitement_demandes(request):
    if request.user.role not in ['AGENT', 'ADMIN']:
        return redirect('dashboard')
        
    demandes = DemandeAttestation.objects.filter(statut='ATTENTE').order_by('-date_depot')
    return render(request, 'certificates/traitement.html', {'demandes': demandes})

@login_required
def traiter_action(request, demande_id):
    if request.user.role not in ['AGENT', 'ADMIN']:
        return redirect('dashboard')

    demande = get_object_or_404(DemandeAttestation, id=demande_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'valider':
            demande.statut = 'VALIDEE'
            demande.save()
            attestation = Attestation.objects.create(demande=demande)
            generer_attestation_pdf(attestation) 
            
            # NEW: Save the action to the audit log
            JournalAction.objects.create(
                utilisateur=request.user,
                action='VALIDATION',
                objet_concerne=f'Demande #{demande.id}',
                detail=f'Attestation {attestation.numero_unique} générée.'
            )
            messages.success(request, "L'attestation a été générée avec succès.")
            
        elif action == 'rejeter':
            demande.statut = 'REJETEE'
            demande.save()
            
            # NEW: Save the rejection to the audit log
            JournalAction.objects.create(
                utilisateur=request.user,
                action='REJET',
                objet_concerne=f'Demande #{demande.id}',
                detail='Demande rejetée par un agent.'
            )
            messages.warning(request, "La demande a été rejetée.")

    return redirect('traitement_demandes')

# Notice: NO @login_required here! This is public.
def verifier_attestation(request, numero_unique):
    try:
        # Look for the certificate by its UUID
        attestation = Attestation.objects.get(numero_unique=numero_unique)
        
        # Check if the document is still valid according to the database
        if attestation.est_valide:
            status = 'valide'
        else:
            status = 'annulee'
            
    except Attestation.DoesNotExist:
        # If someone typed a fake UUID or scanned a broken code
        attestation = None
        status = 'introuvable'
        
    # Send only the minimal necessary data to the public template
    context = {
        'attestation': attestation,
        'status': status
    }
    
    return render(request, 'certificates/verification.html', context)