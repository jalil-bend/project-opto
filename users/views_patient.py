from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from records.models import MedicalRecord

@login_required
def patient_records(request):
    if not request.user.is_patient:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')
    
    records = MedicalRecord.objects.filter(patient__user=request.user).order_by('-created_at')
    return render(request, 'users/patient_records.html', {'records': records})
