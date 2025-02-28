from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    # Add any additional fields here
    is_professional = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_researcher = models.BooleanField(default=False)

class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    access_code = models.CharField(max_length=8, unique=True, null=True)
    code_expiration = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = get_random_string(8)
            self.code_expiration = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def is_code_valid(self):
        return self.code_expiration > timezone.now()

class Researcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True, null=True)
    access_code = models.CharField(max_length=8, unique=True, null=True)
    accessed_codes = models.ManyToManyField(Professional, through='ResearcherAccess')
    research_domain = models.CharField(max_length=100, blank=True, null=True, help_text="Domaine de recherche principal")
    current_projects = models.TextField(blank=True, null=True, help_text="Projets de recherche en cours")
    publications = models.TextField(blank=True, null=True, help_text="Liste des publications")

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = get_random_string(8)
        super().save(*args, **kwargs)



class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('A', 'Autre')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    access_code = models.CharField(max_length=8, unique=True)
    professionals = models.ManyToManyField(Professional, through='PatientProfessional')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = get_random_string(8)
        super().save(*args, **kwargs)


class ResearcherAccess(models.Model):
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    patients = models.ManyToManyField(Patient)
    access_date = models.DateTimeField(auto_now_add=True)

class PatientProfessional(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    access_granted = models.BooleanField(default=False)
    granted_date = models.DateTimeField(auto_now_add=True)

class Discussion(models.Model):
    participants = models.ManyToManyField(User)
    last_activity = models.DateTimeField(auto_now=True)

class Message(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class MedicalRecord(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='medical_records')
    details = models.TextField()
    # Autres champs...
