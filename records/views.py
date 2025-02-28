from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MedicalRecord, MedicalImage, Prescription
from users.models import Patient, Professional
from django.core.exceptions import PermissionDenied

@login_required
def upload_record(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if not hasattr(request.user, 'professional'):
        raise PermissionDenied

    if request.method == 'POST':
        record = MedicalRecord.objects.create(
            patient=patient,
            created_by=request.user.professional,
            description=request.POST.get('description', '')
        )

        if request.FILES.get('file'):
            record.file = request.FILES['file']
            record.save()

        # Gérer les images multiples pour chaque catégorie
        categories = ['topographie', 'oct', 'lampe_a_fente']
        for category in categories:
            files = request.FILES.getlist(f'{category}[]')
            for image_file in files:
                MedicalImage.objects.create(
                    record=record,
                    category=category,
                    image=image_file
                )

        messages.success(request, 'Dossier médical créé avec succès.')
        return redirect('view_records', patient_id=patient.id)

    return render(request, 'records/upload_record.html', {'patient': patient})

@login_required
def patient_records(request):
    if not hasattr(request.user, 'patient'):
        raise PermissionDenied
    
    patient = request.user.patient  # Get the patient instance
    records = MedicalRecord.objects.filter(patient=patient)
    return render(request, 'records/patient_records.html', {
        'records': records,
        'patient': patient,  # Pass the patient instance to the template
        'date_of_birth': patient.date_of_birth  # Pass the patient's date of birth to the template
    })

@login_required
def view_records(request, patient_id):
    # Cette vue est maintenant réservée aux professionnels
    if not hasattr(request.user, 'professional'):
        raise PermissionDenied
        
    patient = get_object_or_404(Patient, id=patient_id)
    records = MedicalRecord.objects.filter(patient=patient)
    
    return render(request, 'records/view_records.html', {
        'patient': patient,
        'records': records,
    })

@login_required
def create_prescription(request, patient_id):
    if not hasattr(request.user, 'professional'):
        raise PermissionDenied

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        medication = request.POST.get('medication')
        dosage = request.POST.get('dosage')
        instructions = request.POST.get('instructions')

        patient = get_object_or_404(Patient, id=patient_id)
        Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage=dosage,
            instructions=instructions
        )

        messages.success(request, 'Ordonnance créée avec succès.')
        return redirect('view_records', patient_id=patient.id)  # Rediriger vers la liste des dossiers médicaux

    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'records/create_prescription.html', {'patient': patient})  # Afficher le formulaire
