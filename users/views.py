from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse

from .models import User, Professional, Patient, Discussion, Message, ResearcherAccess, MedicalRecord
from .forms import UserUpdateForm, PatientUpdateForm, ContactForm  # Ajout du formulaire de contact
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_researcher:
            return reverse('researcher_dashboard')
        elif user.is_professional:
            return reverse('professional_dashboard')
        elif user.is_patient:
            return reverse('patient_dashboard')
        return super().get_success_url()

@login_required
def dashboard(request):
    if request.user.is_professional:
        professional = Professional.objects.get(user=request.user)
        search_query = request.GET.get('search', '')
        
        if search_query:
            patients = Patient.objects.filter(
                professionals=professional,
                user__username__icontains=search_query
            )
        else:
            patients = Patient.objects.filter(professionals=professional)
        
        return render(request, 'users/professional_dashboard.html', {
            'patients': patients,
            'search_query': search_query
        })
    else:
        return patient_dashboard(request)

@login_required
def add_patient(request):
    if not request.user.is_professional:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Validation des données
        if not username or not email:
            messages.error(request, "Le nom d'utilisateur et l'email sont requis")
            return render(request, 'users/add_patient.html')
            
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà")
            return render(request, 'users/add_patient.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà")
            return render(request, 'users/add_patient.html')
        
        try:
            password = get_random_string(10)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_patient=True
            )
            
            patient = Patient.objects.create(user=user)
            professional = Professional.objects.get(user=request.user)
            patient.professionals.add(professional, through_defaults={'access_granted': True})
            
            # Rediriger vers la page d'impression avec les informations
            return render(request, 'users/print_credentials.html', {
                'username': username,
                'password': password,
                'access_code': patient.access_code,
                'generated_date': timezone.now()
            })
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du patient: {str(e)}")
            return render(request, 'users/add_patient.html')
        
    return render(request, 'users/add_patient.html')

@login_required
def grant_access(request):
    if not request.user.is_professional:
        messages.error(request, "Accès non autorisé")
        return redirect('dashboard')

    if request.method == 'POST':
        access_code = request.POST.get('access_code')
        if not access_code:
            messages.error(request, "Le code d'accès est requis")
            return redirect('dashboard')

        try:
            patient = Patient.objects.get(access_code=access_code)
            professional = Professional.objects.get(user=request.user)

            # Vérifier si l'accès existe déjà
            if patient.professionals.filter(id=professional.id).exists():
                messages.warning(request, "Vous avez déjà accès à ce patient")
                return redirect('dashboard')

            patient.professionals.add(professional, through_defaults={'access_granted': True})
            messages.success(request, f"Accès accordé avec succès au patient {patient.user.username}")

        except Patient.DoesNotExist:
            messages.error(request, "Code d'accès invalide")
        except Professional.DoesNotExist:
            messages.error(request, "Erreur de profil professionnel")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")

    return redirect('dashboard')

@login_required
def custom_logout(request):
    logout(request)
    
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if request.user.is_patient:
            patient_form = PatientUpdateForm(request.POST, instance=request.user.patient)
            
            if user_form.is_valid() and patient_form.is_valid():
                try:
                    # Sauvegarde du formulaire utilisateur
                    user = user_form.save()
                    
                    # Sauvegarde du formulaire patient
                    patient = patient_form.save(commit=False)
                    patient.user = user
                    patient.save()
                    
                    
                except Exception as e:
                    messages.error(request, f'Erreur lors de la sauvegarde : {str(e)}')
            else:
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Votre profil a été mis à jour avec succès.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        patient_form = PatientUpdateForm(instance=request.user.patient) if request.user.is_patient else None

    context = {
        'user_form': user_form,
        'patient_form': patient_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def update_profile(request):
    patient_form = None
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if request.user.is_patient:
            patient_form = PatientUpdateForm(request.POST, instance=request.user.patient)
            
            if user_form.is_valid() and patient_form.is_valid():
                try:
                    # Save user form
                    user = user_form.save()
                    
                    # Save patient form
                    patient = patient_form.save(commit=False)
                    patient.user = user
                    patient.save()
                except Exception as e:
                    messages.error(request, f'Erreur lors de la sauvegarde : {str(e)}')
            else:
                messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
        else:
            if user_form.is_valid():
                user_form.save()
        
        if user_form.is_valid() and (request.user.is_patient and patient_form.is_valid() or not request.user.is_patient):
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        patient_form = PatientUpdateForm(instance=request.user.patient) if request.user.is_patient else None

    context = {
        'user_form': user_form,
        'patient_form': patient_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def patient_dashboard(request):
    if not hasattr(request.user, 'patient'):
        return redirect('home')  # Redirect if the user is not a patient
    
    patient = request.user.patient
    
    # Fetch associated health professionals
    professionals = Professional.objects.filter(
        patientprofessional__patient=patient,
        patientprofessional__access_granted=True
    ).select_related('user')
    
    # Fetch any other necessary data, such as medical records
    medical_records = patient.medical_records.all().order_by('-created_at')
    
    context = {
        'user': request.user,
        'patient': patient,
        'professionals': professionals,
        'medical_records': medical_records,
    }
    
    return render(request, 'users/patient_dashboard.html', context)

@login_required
def patient_profile(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        
        # Vérifier si le professionnel a accès à ce patient
        if request.user.is_professional:
            professional = Professional.objects.get(user=request.user)
            if not patient.professionals.filter(id=professional.id).exists():
                messages.error(request, "Vous n'avez pas accès à ce patient")
                return redirect('dashboard')
        # Si c'est un patient, vérifier que c'est bien son propre profil
        elif request.user.is_patient and request.user.patient.id != patient_id:
            messages.error(request, "Vous n'avez pas accès à ce profil")
            return redirect('dashboard')
            
        return render(request, 'users/patient_profile.html', {
            'patient': patient
        })
    except Patient.DoesNotExist:
        messages.error(request, "Patient non trouvé")
        return redirect('dashboard')

def TermsAndConditions(request):
    
    return render(request, 'users/terms-and-conditions.html')

@login_required
def discussions_list(request):
    discussions = Discussion.objects.filter(participants=request.user).order_by('-last_activity')
    unread_counts = {discussion.id: discussion.messages.filter(read=False).count() for discussion in discussions}
    print(f"Nombre de discussions: {discussions.count()}")  # Debug
    print(f"Discussions: {[discussion.id for discussion in discussions]}")  # Debug
    print(f"Unread counts: {unread_counts}")  # Debug
    return render(request, 'users/discussions_list.html', {
        'discussions': discussions,
        'unread_counts': unread_counts,
    })

@login_required
def chat_view(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    messages = discussion.messages.all().order_by('timestamp')
    return render(request, 'users/chat.html', {
        'discussion': discussion,
        'messages': messages
    })

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        discussion_id = request.POST.get('discussion_id')
        discussion = get_object_or_404(Discussion, id=discussion_id)
        
        if request.user not in discussion.participants.all():
            return JsonResponse({'success': False, 'error': 'Non autorisé'})
        
        file = request.FILES['file']
        message = Message.objects.create(
            discussion=discussion,
            sender=request.user,
            file=file
        )
        return JsonResponse({'success': True, 'file_url': message.file.url})
    return JsonResponse({'success': False, 'error': 'Fichier non fourni'})

@login_required
def create_discussion(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    discussion = Discussion.objects.create()
    discussion.participants.add(request.user, other_user)
    return redirect('chat', discussion_id=discussion.id)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def change_password_professional(request):
    if not request.user.is_professional:
       
        return redirect('home')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password_professional.html', {'form': form})

@login_required
def change_password_patient(request):
    if not request.user.is_patient:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password_patient.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Envoyer l'email
            send_mail(
                f'Contact Form Submission from {name}',
                message,
                email,  # Email de l'expéditeur
                ['your-email@example.com'],  # Email du destinataire
                fail_silently=False,
            )
            return redirect('success')  # Rediriger vers une page de succès ou afficher un message
    else:
        form = ContactForm()
    return render(request, 'index.html', {'form': form})

@login_required
def admin_dashboard(request):
    users = User.objects.all()  # Fetch all users

    # Check for search query
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(username__icontains=search_query)  # Filter users by username

    context = {
        'users': users,
        'search_query': search_query,
    }

    return render(request, 'users/admin_dashboard.html', context)

@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created successfully!')
            return redirect('admin_dashboard')  # Redirect to admin dashboard after successful creation
    else:
        form = UserCreationForm()
    return render(request, 'users/add_user.html', {'form': form})

@login_required
def manage_users(request):
    users = User.objects.all()  # Fetch all users

    # Check for search query
    search_query = request.GET.get('search')
    print(f"Search Query: {search_query}")  # Debug statement
    if search_query:
        users = users.filter(username__icontains=search_query) | \
                 users.filter(email__icontains=search_query) | \
                 users.filter(first_name__icontains=search_query) | \
                 users.filter(last_name__icontains=search_query)  # Filter users by username, email, first name, and last name

    print(f"Number of Users Found: {users.count()}")  # Debug statement
    return render(request, 'users/manage_users.html', {'users': users, 'search_query': search_query})

@login_required
def view_user(request, user_id):
    user = User.objects.get(id=user_id)  # Fetch the user by ID
    return render(request, 'users/view_user.html', {'user': user})

@login_required
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)  # Fetch the user by ID
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('manage_users')  # Redirect to manage users after successful update
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/edit_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)  # Fetch the user by ID
    user.delete()  # Delete the user
    messages.success(request, 'User deleted successfully!')
    return redirect('manage_users')  # Redirect to manage users after deletion

@login_required
def professional_dashboard(request):
    professional = Professional.objects.get(user=request.user)  # Fetch the professional instance
    patients = Patient.objects.filter(professionals=professional)  # Fetch associated patients

    # Check for search query
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(user__username__icontains=search_query)  # Filter patients by username

    context = {
        'professional': professional,
        'patients': patients,
        'search_query': search_query,
    }

    return render(request, 'users/professional_dashboard.html', context)

@login_required
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Rediriger vers le tableau de bord si l'utilisateur est connecté
    return render(request, 'users/home.html')

@login_required
def researcher_access(request):
    if not request.user.is_researcher:
        return redirect('login')
    
    attempts = cache.get(f'access_attempts_{request.user.id}', 0)
    if attempts >= 5:
        return render(request, 'researcher/access_form.html', {'error': 'Trop de tentatives (max 5)'})
    
    if request.method == 'POST':
        code = request.POST.get('access_code')
        try:
            professional = Professional.objects.get(access_code=code)
            if not professional.is_code_valid():
                error = "Code expiré"
                return render(request, 'researcher/access_form.html', {'error': error})
            
            ResearcherAccess.objects.create(
                researcher=request.user.researcher,
                professional=professional
            )
            return redirect('researcher_dashboard')
        except Professional.DoesNotExist:
            cache.set(f'access_attempts_{request.user.id}', attempts + 1, timeout=3600)
            error = "Code d'accès invalide"
            return render(request, 'researcher/access_form.html', {'error': error})
    
    return render(request, 'researcher/access_form.html')

@login_required
def researcher_dashboard(request):
    if request.method == 'POST':
        license_number = request.POST.get('license_number')
        access_code = request.POST.get('access_code')
        
        print(f"Numéro de Licence saisi : {license_number}")  # Message de débogage
        print(f"Code d'Accès saisi : {access_code}")  # Message de débogage
        
        try:
            professional = Professional.objects.get(license_number=license_number, access_code=access_code)
            researcher = request.user.researcher
            if ResearcherAccess.objects.filter(researcher=researcher, professional=professional).exists():
                print(f"Professionnel trouvé : {professional.user.username}, Licence : {professional.license_number}")  # Message de débogage
                print(f"Objet Professional : {professional}")  # Message de débogage
                return render(request, 'researcher/professional_records.html', {'professional': professional})
            else:
                return render(request, 'researcher/dashboard.html', {'error': 'Accès non autorisé à ce professionnel'})
        except Professional.DoesNotExist:
            return render(request, 'researcher/dashboard.html', {'error': 'Numéro de licence ou code d\'accès invalide'})
    return render(request, 'researcher/dashboard.html')

from records.models import MedicalRecord

@csrf_protect
@login_required
def view_patient_records(request):
    if request.method == 'POST':
        access_code = request.POST.get('access_code')
        professional = Professional.objects.filter(access_code=access_code).first()
        
        if professional:
            patients = Patient.objects.filter(patientprofessional__professional=professional)
            medical_records = MedicalRecord.objects.filter(
                patient__in=patients,
                professional=professional
            )
            return render(request, 'researcher/professional_records.html', {
                'records': medical_records,
                'professional': professional
            })
    
    return render(request, 'researcher/professional_records.html', {'error': 'Accès refusé'})

@login_required
def access_projects(request):
    print("Vue access_projects appelée")  # Message de débogage
    if request.method == 'POST':
        form = AccessCodeForm(request.POST)
        if form.is_valid():
            access_code = form.cleaned_data['access_code']
            print(f"Code d'accès saisi : {access_code}")  # Message de débogage
            
            # Afficher tous les professionnels pour débogage
            all_professionals = Professional.objects.all()
            print("Professionnels disponibles :")
            for professional in all_professionals:
                print(f"Nom: {professional.user.username}, Code d'accès: {professional.access_code}")

            try:
                professional = Professional.objects.get(access_code=access_code)
                medical_records = MedicalRecord.objects.filter(professional=professional)
                print(f"Nombre de dossiers médicaux trouvés : {medical_records.count()}")  # Debugging output
                for record in medical_records:
                    print(f"Détails du dossier : {record.details}")  # Debugging output
                return render(request, 'researcher/professional_records.html', {'professional': professional, 'records': medical_records})
            except Professional.DoesNotExist:
                print("Code d'accès invalide")  # Message de débogage
                return render(request, 'researcher/dashboard.html', {'error': 'Code d\'accès invalide'})
    else:
        form = AccessCodeForm()
    return render(request, 'researcher/access_projects.html', {'form': form})

@login_required
def access_patient_records(request):
    if request.method == 'POST':
        access_code = request.POST.get('access_code')
        try:
            professional = Professional.objects.get(access_code=access_code)
            records = PatientRecord.objects.filter(professional=professional)
            return render(request, 'researcher/dashboard.html', {'records': records})
        except Professional.DoesNotExist:
            return render(request, 'researcher/dashboard.html', {'error': 'Invalid access code'})
    return render(request, 'researcher/dashboard.html')

@login_required
def consult_data(request):
    # Logique pour consulter les données
    return render(request, 'researcher/data.html')